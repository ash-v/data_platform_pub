## THIS FUNCTION POPULATES APP DB I.E. DYNAMODB FROM ORG. DOMAIN DATA

# 1. lambda function 
# 2. role
# 3. Assume assume policy
# 4. Cloud watch policy to the role 
 

resource "aws_lambda_function" "lambda_cron_orgdomain_to_appdb" {
  filename      = "./modules/cron-orgdomain-to-appdb/lambda_function.zip"
  function_name = "${var.lambda_function_name}"
  role          = aws_iam_role.role_lambda_cron_orgdomain_to_appdb.arn
  handler       = "lambda_function.lambda_handler"

  layers = ["arn:aws:lambda:us-east-1:672446792193:layer:postsetlambda-pset:5", # for dynamodbgeo
            "arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p38-pandas:1",
            "arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p38-lxml:1"]

  runtime = "python3.8"

  memory_size = "500" # 500 mb
  timeout = "300" # 5mins
}

# 3. Assume policy
resource "aws_iam_role" "role_lambda_cron_orgdomain_to_appdb" { # role_<lambda name>
  name = "role_lambda_cron_orgdomain_to_appdb"
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
resource "aws_iam_policy" "policy_lambda_cron_orgdomain_to_appdb" {
  name        = "policy_lambda_cron_orgdomain_to_appdb"
  path        = "/"
  description = "IAM policy for lambda_cron_orgdomain_to_appdb lambda"

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
            "dynamodb:Put*",
            "dynamodb:Create*",
            "dynamodb:BatchWriteItem",
            "dynamodb:Get*",
            "dynamodb:BatchGetItem",
            "dynamodb:List*",
            "dynamodb:Describe*",
            "dynamodb:Scan",
            "dynamodb:Query",
            "dynamodb:Update*",
            "dynamodb:RestoreTable*"
        ],
        "Resource": [
            "arn:aws:dynamodb:us-east-1:672446792193:table/peeeqPosts-dev",
            "arn:aws:dynamodb:us-east-1:672446792193:table/peeeqPosts-dev/index/*"
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
resource "aws_iam_role_policy_attachment" "lambda_cron_orgdomain_to_appdb_logs" {
  role       = aws_iam_role.role_lambda_cron_orgdomain_to_appdb.name
  policy_arn = aws_iam_policy.policy_lambda_cron_orgdomain_to_appdb.arn
}


# Eventbridge / Cloudwatch event
resource "aws_cloudwatch_event_rule" "cron_orgdomain_to_appdb_once_a_day" {
    name = "cron_orgdomain_to_appdb_once_a_day"
    description = "Fires once a day to populate appdb"
    schedule_expression = "cron(00 16 * * ? *)"  ## runs every day at 3:45 pm UTC (11:45 am et)
}  

# Add lambda function as target for cron event
resource "aws_cloudwatch_event_target" "check_cron_orgdomain_to_appdb_once_a_day" {
    rule = aws_cloudwatch_event_rule.cron_orgdomain_to_appdb_once_a_day.name
    target_id = "lambda_cron_orgdomain_to_appdb"
    arn = aws_lambda_function.lambda_cron_orgdomain_to_appdb.arn
}

# lambda permits events from eventbridge/cloudwatch
resource "aws_lambda_permission" "allow_cloudwatch_to_call_cron_orgdomain_to_appdb" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.lambda_cron_orgdomain_to_appdb.function_name
    principal = "events.amazonaws.com"
    source_arn = "${aws_cloudwatch_event_rule.cron_orgdomain_to_appdb_once_a_day.arn}"
}

