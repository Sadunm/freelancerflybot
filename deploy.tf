# Terraform configuration for deploying FreelancerFly Bot to AWS

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_name" {
  description = "Name of the SSH key pair"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID"
  type        = string
}

# Security group
resource "aws_security_group" "freelancerfly_bot_sg" {
  name        = "freelancerfly_bot_sg"
  description = "Security group for FreelancerFly Bot"
  vpc_id      = var.vpc_id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "freelancerfly_bot_sg"
  }
}

# EC2 instance
resource "aws_instance" "freelancerfly_bot" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.freelancerfly_bot_sg.id]
  subnet_id              = var.subnet_id

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  tags = {
    Name = "freelancerfly_bot"
  }

  # User data script to set up the instance
  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y docker.io docker-compose git
              systemctl enable docker
              systemctl start docker
              
              # Clone repository
              git clone https://github.com/yourusername/freelancerfly_bot.git /opt/freelancerfly_bot
              
              # Create config files
              mkdir -p /opt/freelancerfly_bot/config
              
              # Set up cron job to start bot on reboot
              echo "@reboot cd /opt/freelancerfly_bot && docker-compose up -d" | crontab -
              
              # Start the bot
              cd /opt/freelancerfly_bot
              docker-compose up -d
              EOF
}

# Latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Output
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.freelancerfly_bot.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.freelancerfly_bot.public_ip
}