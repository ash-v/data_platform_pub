module "cron_hotfix_orgdomain_to_appdb_devtest" {
    source = "./modules/cron-hotfix-orgdomain-to-appdb-devtest/"   
    lambda_function_name = "cron-hotfix-orgdomain-to-appdb-devtest"
}

