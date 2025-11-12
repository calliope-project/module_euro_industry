
rule prepare_ammonia_production:
    input:
        usgs=rules.download_usgs_ammonia.output.file,
    output:
        prepared="resources/automatic/prepared/ammonia_production.csv",
    log:
        "logs/prepare/prepare_ammonia_production.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_ammonia_production.py"


rule prepare_aggregated_production:
    params:
        industry=config["industry"],
        countries=config["countries"],
    input:
        ch_industrial_production=rules.download_CHE_industry.output.file,
        ammonia_production=rules.prepare_ammonia_production.output.prepared,
        jrc_dir="resources/automatic/jrc_idees/",
        eurostat_dir="resources/automatic/eurostat/",
    output:
        production_per_country="results/aggregated/production_per_country.csv",
    log:
        "logs/prepare/aggregated_production.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_aggregated_production.py"
