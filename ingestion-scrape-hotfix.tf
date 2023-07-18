module "scrape_hotfix" {
    source = "./modules/data_ingestion/scrapper_hotfix/"   
    lambda_function_name = "scrape-hotfix-target-to-rawzone"
}

