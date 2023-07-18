module "scrape_syracusetriviacompany" {
    source = "./modules/data_ingestion/scrapper_syracusetriviacompany/"   
    lambda_function_name = "scrape-syracusetriviacompany-to-rawzone"
}

