output "storage" {
    value = {
        rawzone = module.rawzone.bucket_name
        organizedzone = module.organizedzone.bucket_name
    }
}

