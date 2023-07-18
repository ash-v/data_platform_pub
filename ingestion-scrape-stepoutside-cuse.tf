module "scrape_stepoutside_cuse" {
    source = "./modules/data_ingestion/scrapper_stepoutside_cuse/"   
    lambda_function_name = "scrape-stepoutsidecuse-to-rawzone"
}

