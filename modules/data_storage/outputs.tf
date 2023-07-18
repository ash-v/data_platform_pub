output "bucket_id" {
    description = "s3 bucket id"
    value = aws_s3_bucket.base.id
}

output "bucket_arn" {
    description = "s3 bucket ard"
    value = aws_s3_bucket.base.arn
}

output "bucket_name" {
    description = "s3 bucket name"
    value = aws_s3_bucket.base.bucket
}
