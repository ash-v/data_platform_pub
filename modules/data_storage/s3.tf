resource "aws_s3_bucket" "base" {
  bucket = "${var.bucket_name}"
}

# all bucket will be private
resource "aws_s3_bucket_acl" "base_acls" {
  bucket = aws_s3_bucket.base.id
  acl    = "private"
}


