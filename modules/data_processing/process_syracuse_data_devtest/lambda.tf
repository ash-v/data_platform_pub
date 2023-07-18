# 1. lambda function 
# 2. role
# 3. Assume assume policy
# 4. Cloud watch policy to the role 
 

resource "aws_lambda_function" "lambda_process_syracuse_data_devtest" {
  filename      = "./modules/data_processing/process_syracuse_data_devtest/lambda_function.zip"
  function_name = "${var.lambda_function_name}"
  role          = aws_iam_role.role_lambda_process_syracuse_data_devtest.arn
  handler       = "lambda_function.lambda_handler"

  layers = ["arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p38-pandas:1",
            "arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p38-lxml:1"]

  runtime = "python3.8"

  memory_size = "1024" # 500 mb
  timeout = "600" # 10mins
}

# 3. Assume policy
resource "aws_iam_role" "role_lambda_process_syracuse_data_devtest" { # role_<lambda name>
  name = "role_lambda_process_syracuse_data_devtest"
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
resource "aws_iam_policy" "policy_lambda_process_syracuse_data_devtest" {
  name        = "policy_lambda_process_syracuse_data_devtest"
  path        = "/"
  description = "IAM policy for lambda_process_syracuse_data_devtest lambda"

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
    }
  ]
}
EOF
}
# attach policy to lambda role
resource "aws_iam_role_policy_attachment" "lambda_process_syracuse_data_logs_devtest" {
  role       = aws_iam_role.role_lambda_process_syracuse_data_devtest.name
  policy_arn = aws_iam_policy.policy_lambda_process_syracuse_data_devtest.arn
}


# Eventbridge / Cloudwatch event
resource "aws_cloudwatch_event_rule" "process_syracuse_data_once_a_day_devtest" {
    name = "process_syracuse_once_a_days_devtest"
    description = "Fires once a day to scrape data in syracuse"
    schedule_expression = "cron(30 15 * * ? *)"  ## runs every day at 3:30 pm UTC (11:30 am et)
}  

# Add lambda function as target for cron event
resource "aws_cloudwatch_event_target" "check_process_syracuse_data_once_a_day_devtest" {
    rule = aws_cloudwatch_event_rule.process_syracuse_data_once_a_day_devtest.name
    target_id = "lambda_scrape_funknwaffles_devtest"
    arn = aws_lambda_function.lambda_process_syracuse_data_devtest.arn
}

# lambda permits events from eventbridge/cloudwatch
resource "aws_lambda_permission" "allow_cloudwatch_to_call_process_syracuse_data_devtest" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.lambda_process_syracuse_data_devtest.function_name
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.process_syracuse_data_once_a_day_devtest.arn}"
}

