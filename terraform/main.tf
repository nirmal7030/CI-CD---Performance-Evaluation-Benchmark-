terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "cicd-new"  # <— uses your named AWS CLI profile
}

# Use the default VPC + one subnet
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Group: HTTP open (80); SSH optional (lock to your IP ideally)
resource "aws_security_group" "web_sg" {
  name        = "${var.project_name}-sg"
  description = "Allow HTTP and (optional) SSH"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAM role so EC2 has SSM (no SSH keys needed)
data "aws_iam_policy_document" "ec2_trust" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2_role" {
  name               = "${var.project_name}-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_trust.json
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# Latest Amazon Linux 2023 AMI
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["137112412989"] # Amazon

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# User data to install Docker, clone repo, build and run container
locals {
  user_data = <<-EOF
    #!/bin/bash
    set -e
    dnf update -y
    dnf install -y docker git
    systemctl enable docker
    systemctl start docker

    cd /opt
    if [ ! -d cicd-benchmark ]; then
      git clone https://github.com/${var.github_user}/${var.github_repo}.git cicd-benchmark
    else
      cd cicd-benchmark
      git pull --rebase || true
      cd ..
    fi
    cd cicd-benchmark

    /usr/bin/docker build -t cicd-benchmark:prod .
    /usr/bin/docker rm -f cicdbench || true

    /usr/bin/docker run -d --name cicdbench -p 80:8000 \
      -e DEBUG=0 \
      -e SECRET_KEY="${var.secret_key}" \
      -e ALLOWED_HOSTS="*" \
      -e BENCH_API_KEY="${var.bench_api_key}" \
      cicd-benchmark:prod
  EOF
}

resource "aws_instance" "web" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.web_sg.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2_profile.name
  associate_public_ip_address = true
  user_data                   = local.user_data

  tags = {
    Name = var.project_name
  }
}
