resource "aws_vpc" "image_processing_lambda" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main_image_processing_lambda" {
  vpc_id     = aws_vpc.image_processing_lambda.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "main"
  }
  # route table currently not tracked in TF
}

resource "aws_subnet" "private1_image_processing_lambda" {
  vpc_id     = aws_vpc.image_processing_lambda.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "private 1"
  }
  # route table currently not tracked in TF
}

resource "aws_subnet" "private2_image_processing_lambda" {
  vpc_id     = aws_vpc.image_processing_lambda.id
  cidr_block = "10.0.3.0/24"
  availability_zone = "us-east-1c"

  tags = {
    Name = "private 2"
  }
  # route table currently not tracked in TF
}


resource "aws_security_group" "sg_image_processing_lambda" {
  name        = "sg_image_processing_lambda"
  description = "sg_image_processing_lambda inbound & outbound traffic"
  vpc_id      = aws_vpc.image_processing_lambda.id

  ingress {
    description      = ""
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    description      = ""
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    description      = "Allow all traffic within this SG"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = [aws_vpc.image_processing_lambda.cidr_block]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

}

# Create the IGW and connect to VPC
resource "aws_internet_gateway" "igw_lambda_vpc" {
  vpc_id = aws_vpc.image_processing_lambda.id

}