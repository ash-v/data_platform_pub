module "cron_orgdomain_to_appdb" {
    source = "./modules/cron-orgdomain-to-appdb/"   
    lambda_function_name = "cron-orgdomain-to-appdb"
}

