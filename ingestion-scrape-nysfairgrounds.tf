module "scrape_nysfairgrounds" {
    source = "./modules/data_ingestion/scrapper_nysfairgrounds/"   
    lambda_function_name = "scrape-nysfairgrounds-to-rawzone"
}

