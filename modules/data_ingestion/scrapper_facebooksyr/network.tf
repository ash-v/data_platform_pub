resource "aws_vpc" "facebook_scrappers" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main_facebook_scrappers" {
  vpc_id     = aws_vpc.facebook_scrappers.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "main"
  }
  # route table currently not tracked in TF
}

resource "aws_subnet" "private1_facebook_scrappers" {
  vpc_id     = aws_vpc.facebook_scrappers.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "private 1"
  }
  # route table currently not tracked in TF
}

resource "aws_subnet" "private2_facebook_scrappers" {
  vpc_id     = aws_vpc.facebook_scrappers.id
  cidr_block = "10.0.3.0/24"
  availability_zone = "us-east-1c"

  tags = {
    Name = "private 2"
  }
  # route table currently not tracked in TF
}


resource "aws_security_group" "sg_facebook_scrappers" {
  name        = "sg_facebook_scrappers"
  description = "sg_facebook_scrappers inbound & outbound traffic"
  vpc_id      = aws_vpc.facebook_scrappers.id

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
    cidr_blocks      = [aws_vpc.facebook_scrappers.cidr_block]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

}

# Create the IGW and connect to VPC
resource "aws_internet_gateway" "igw_facebook_scrappers_vpc" {
  vpc_id = aws_vpc.facebook_scrappers.id

}