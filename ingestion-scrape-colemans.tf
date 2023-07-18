module "scrape_colemans" {
    source = "./modules/data_ingestion/scrapper_colemans/"   
    lambda_function_name = "scrape-colemans-to-rawzone"
}

