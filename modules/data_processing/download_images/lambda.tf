# 1. lambda function 
# 2. role
# 3. Assume assume policy
# 4. Cloud watch policy to the role 
 

resource "aws_lambda_function" "lambda_download_images" {
  filename      = "./modules/data_processing/download_images/lambda_function.zip"
  function_name = "${var.lambda_function_name}"
  role          = aws_iam_role.role_lambda_download_images.arn
  handler       = "lambda_function.lambda_handler"

  layers = [
            "arn:aws:lambda:us-east-1:770693421928:layer:Klayers-python38-libgthread-so:1",
            "arn:aws:lambda:us-east-1:770693421928:layer:Klayers-python38-opencv-python-headless:11"
            ]

  runtime = "python3.8"

  memory_size = "1024" # 500 mb
  timeout = "600" # 10mins

  vpc_config {
    # Every subnet should be able to reach an EFS mount target in the same Availability Zone. Cross-AZ mounts are not permitted.
    subnet_ids         = [aws_subnet.private1_image_processing_lambda.id]
    security_group_ids = [aws_security_group.sg_image_processing_lambda.id]
  }

  file_system_config {
    # EFS file system access point ARN
    arn = aws_efs_access_point.access_point_for_lambda.arn

    # Local mount path inside the lambda function. Must start with '/mnt/'.
    local_mount_path = "/mnt/efs"
  }


}

# 3. Assume policy
resource "aws_iam_role" "role_lambda_download_images" { # role_<lambda name>
  name = "role_lambda_download_images"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# 4. Cloud watch policy to the role
resource "aws_iam_policy" "policy_lambda_download_images" {
  name        = "policy_lambda_download_images"
  path        = "/"
  description = "IAM policy for lambda_download_images lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Effect": "Allow",
        "Action": "logs:CreateLogGroup",
        "Resource": "arn:aws:logs:us-east-1:672446792193:*"
    },
    {
        "Effect": "Allow",
        "Action": [
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ],
        "Resource": [
            "arn:aws:logs:us-east-1:672446792193:log-group:/aws/lambda/${var.lambda_function_name}:*"
        ]
    },
    {
        "Effect": "Allow",
        "Action": [
            "s3:*"
        ],
        "Resource": "arn:aws:s3:::*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeNetworkInterfaces",
        "ec2:CreateNetworkInterface",
        "ec2:DeleteNetworkInterface",
        "ec2:DescribeInstances",
        "ec2:AttachNetworkInterface"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}
# attach policy to lambda role
resource "aws_iam_role_policy_attachment" "lambda_download_images_logs" {
  role       = aws_iam_role.role_lambda_download_images.name
  policy_arn = aws_iam_policy.policy_lambda_download_images.arn
}


# Eventbridge / Cloudwatch event
resource "aws_cloudwatch_event_rule" "download_images_once_a_day" {
    name = "download_images_once_a_days"
    description = "Fires once a day to download images"
    schedule_expression = "cron(00 16 * * ? *)"  ## runs every day at 3:45 pm UTC (11:45 am et)
}  

# Add lambda function as target for cron event
resource "aws_cloudwatch_event_target" "check_download_images_once_a_day" {
    rule = aws_cloudwatch_event_rule.download_images_once_a_day.name
    target_id = "lambda_download_images"
    arn = aws_lambda_function.lambda_download_images.arn
}

# lambda permits events from eventbridge/cloudwatch
resource "aws_lambda_permission" "allow_cloudwatch_to_call_download_images" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.lambda_download_images.function_name
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.download_images_once_a_day.arn}"
}

