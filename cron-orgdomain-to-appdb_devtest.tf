module "cron_orgdomain_to_appdb_devtest" {
    source = "./modules/cron-orgdomain-to-appdb-devtest/"   
    lambda_function_name = "cron-orgdomain-to-appdb-devtest"
}

