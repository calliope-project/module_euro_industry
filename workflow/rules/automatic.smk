"""Rules to used to download automatic resource files."""


rule download_eurostat:
    message:
        "Download stable Eurostat energy balances."
    params:
        url=internal["resources"]["automatic"]["eurostat"],
    output:
        file="resources/automatic/eurostat.zip",
    log:
        "logs/automatic/download_eurostat.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'

rule download_jrc_idees:
    message:
        "Download the JRC IDEES dataset."
    params:
        url=internal["resources"]["automatic"]["jrc_idees"],
    output:
        file="resources/automatic/jrc_idees.zip",
    log:
        "logs/automatic/download_jrc_idees.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_hotmaps:
    message:
        "Download the Hotmaps energy intensive industry dataset."
    params:
        url=internal["resources"]["automatic"]["hotmaps"],
    output:
        file="resources/automatic/hotmaps.csv",
    log:
        "logs/automatic/download_hotmaps.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_usgs_ammonia:
    message:
        "Download the U.S. geological survey on ammonia supply."
    params:
        url=internal["resources"]["automatic"]["usgs_ammonia"],
    output:
        file="resources/automatic/usgs_ammonia.xlsx",
    log:
        "logs/automatic/download_usgs_ammonia.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_GEM_SPT:
    message:
        "Download the Global Energy Monitor - Steel Plant Tracker."
    params:
        url=internal["resources"]["automatic"]["GEM_SPT"],
    output:
        file="resources/automatic/GEM_SPT.xlsx",
    log:
        "logs/automatic/download_GEM_SPT.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'

rule download_CHE_industry:
    message:
        "Download CHE industrial production per subsector."
    params:
        url=internal["resources"]["automatic"]["CHE_industry"],
    output:
        file="resources/automatic/CHE_industry.csv",
    log:
        "logs/automatic/download_CHE_industry.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'

