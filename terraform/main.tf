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
  profile = "cicd-new"
}

# ---- Data: Default VPC + all subnets ----
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Look up each subnet to get its availability_zone
data "aws_subnet" "all" {
  for_each = toset(data.aws_subnets.default.ids)
  id       = each.value
}

# Pick any AZ except 1e (t3.small not available for your account there)
locals {
  project_name  = var.project_name
  preferred_azs = ["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1f"]
  good_subnet_ids = [
    for s in data.aws_subnet.all : s.id
    if contains(local.preferred_azs, s.availability_zone)
  ]
  chosen_subnet_id = length(local.good_subnet_ids) > 0 ? local.good_subnet_ids[0] : data.aws_subnets.default.ids[0]
}

# ---- Security Group ----
resource "aws_security_group" "web_sg" {
  name        = "${local.project_name}-sg"
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
    # lock down later to your IP; for now keep closed by default:
    cidr_blocks = ["0.0.0.0/32"]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---- IAM for SSM on EC2 ----
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
  name               = "${local.project_name}-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_trust.json
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${local.project_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# ---- Latest Amazon Linux 2023 AMI ----
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["137112412989"] # Amazon
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# ---- EC2 user-data (installs Docker + SSM, runs your app) ----
locals {
  user_data = <<-EOF
    #!/bin/bash
    set -e

    # Update and install Docker, Git, SSM Agent
    dnf update -y
    dnf install -y docker git amazon-ssm-agent

    # Enable services
    systemctl enable docker
    systemctl start docker
    systemctl enable amazon-ssm-agent
    systemctl start  amazon-ssm-agent

    # Fetch app code
    cd /opt
    if [ ! -d cicd-benchmark ]; then
      git clone https://github.com/${var.github_user}/${var.github_repo}.git cicd-benchmark
    else
      cd cicd-benchmark
      git pull --rebase || true
      cd ..
    fi
    cd cicd-benchmark

    # Build & run container
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

# ---- EC2 instance (now using a supported AZ) ----
resource "aws_instance" "web" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = var.instance_type
  subnet_id                   = local.chosen_subnet_id
  vpc_security_group_ids      = [aws_security_group.web_sg.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2_profile.name
  associate_public_ip_address = true
  user_data                   = local.user_data

  # Recreate instance automatically if user_data changes
  user_data_replace_on_change = true

  tags = {
    Name = local.project_name
  }
}

# ---- Helpful outputs ----
output "public_ip" { value = aws_instance.web.public_ip }
output "public_dns" { value = aws_instance.web.public_dns }
output "http_url" { value = "http://${aws_instance.web.public_dns}/" }
output "instance_id" { value = aws_instance.web.id }
