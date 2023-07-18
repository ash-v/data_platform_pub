# EFS file system
resource "aws_efs_file_system" "efs_for_facebook_scrappers" {
  tags = {
    Name = "efs_for_facebook_scrapper_lambda"
  }

  availability_zone_name = "us-east-1b"  # private subnet because lambda will need to be in provate subnet so that it can connect to internet
}

# Mount target connects the file system to the subnet
resource "aws_efs_mount_target" "mount_target_for_facebook_scrapper" {
  file_system_id  = aws_efs_file_system.efs_for_facebook_scrappers.id
  subnet_id       = aws_subnet.private1_facebook_scrappers.id
  security_groups = [aws_security_group.sg_facebook_scrappers.id]
 # availability_zone_name = "us-east-1a"
}

# EFS access point used by lambda file system
resource "aws_efs_access_point" "access_point_for_lambda" {
  file_system_id = aws_efs_file_system.efs_for_facebook_scrappers.id

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