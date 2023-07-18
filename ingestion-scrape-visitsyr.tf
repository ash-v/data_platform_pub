module "scrape_visitsyr" {
    source = "./modules/data_ingestion/scrapper_visitsyr/"   
    lambda_function_name = "scrape-visitsyr-to-rawzone"
}

