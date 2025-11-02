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
  profile = "cicd-new" # uses your named CLI profile
}

# ----- Networking: use default VPC + one subnet -----
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "web_sg" {
  name        = "${var.project_name}-sg"
  description = "Allow HTTP and (optional) SSH"
  vpc_id      = data.aws_vpc.default.id

  # HTTP
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH (effectively blocked by default 0.0.0.0/32; set to your_ip/32 if needed)
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
  }

  # Egress all
  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ----- IAM for EC2 to be SSM-managed -----
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

# ----- AMI -----
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["137112412989"] # Amazon

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# ----- User data (install/enable SSM Agent, Docker, run app) -----
locals {
  user_data = <<-EOF
    #!/bin/bash
    set -e

    # Base updates + tools
    dnf update -y
    dnf install -y docker git

    # Ensure SSM Agent is installed & running (AL2023 usually has it, force-install to be safe)
    dnf install -y amazon-ssm-agent || true
    systemctl enable amazon-ssm-agent
    systemctl restart amazon-ssm-agent

    # Docker
    systemctl enable docker
    systemctl start docker

    # App code
    cd /opt
    if [ ! -d cicd-benchmark ]; then
      git clone https://github.com/${var.github_user}/${var.github_repo}.git cicd-benchmark
    else
      cd cicd-benchmark
      git pull --rebase || true
      cd ..
    fi
    cd cicd-benchmark

    # Build + run container
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

# ----- EC2 instance -----
resource "aws_instance" "web" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.web_sg.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2_profile.name
  associate_public_ip_address = true
  user_data                   = local.user_data

  user_data_replace_on_change = true

  tags = {
    Name = var.project_name
  }
}
