module "scrape_cnyarts" {
    source = "./modules/data_ingestion/scrapper_cnyarts/"   
    lambda_function_name = "scrape-cnyarts-to-rawzone"
}

