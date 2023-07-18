# EFS file system
resource "aws_efs_file_system" "efs_for_image_processing_lambda" {
  tags = {
    Name = "efs_for_image_processing_lambda"
  }

  availability_zone_name = "us-east-1b"
}

# Mount target connects the file system to the subnet
resource "aws_efs_mount_target" "alpha" {
  file_system_id  = aws_efs_file_system.efs_for_image_processing_lambda.id
  subnet_id       = aws_subnet.private1_image_processing_lambda.id
  security_groups = [aws_security_group.sg_image_processing_lambda.id]
 # availability_zone_name = "us-east-1a"
}

# EFS access point used by lambda file system
resource "aws_efs_access_point" "access_point_for_lambda" {
  file_system_id = aws_efs_file_system.efs_for_image_processing_lambda.id

  root_directory {
    path = "/efs"
    creation_info {
      owner_gid   = 1000
      owner_uid   = 1000
      permissions = "777"
    }
  }

  posix_user {
    gid = 1000
    uid = 1000
  }
}