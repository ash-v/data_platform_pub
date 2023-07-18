module "organizedzone" {
    source = "./modules/data_storage/"
    #bucket name should be unique
    bucket_name = "peeeq-datalake-organized-zone"       
}



