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


rule download_ammonia_usgs:
    message:
        "Download the U.S. geological survey on ammonia supply."
    params:
        url=internal["resources"]["automatic"]["ammonia"]["usgs"],
    output:
        file="resources/automatic/ammonia/usgs.xlsx",
    log:
        "logs/automatic/download_ammonia_usgs.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_ammonia_plants:
    message:
        "Download ammonia plants as collected by PyPSA-Eur."
    params:
        url=internal["resources"]["automatic"]["ammonia"]["plants"]
    output:
        file="resources/automatic/ammonia/plants.csv",
    log:
        "logs/automatic/download_ammonia_plants.log",
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


rule download_cement_non_eu:
    message:
        "Download cement plants as collected by PyPSA-Eur."
    params:
        url=internal["resources"]["automatic"]["non_eu"]["cement"],
    output:
        file="resources/automatic/cement_non_eu.csv",
    log:
        "logs/automatic/download_cement_non_eu.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_refineries_non_eu:
    message:
        "Download refineries as collected by PyPSA-Eur."
    params:
        url=internal["resources"]["automatic"]["non_eu"]["refineries"],
    output:
        file="resources/automatic/non_eu/refineries.csv",
    log:
        "logs/automatic/download_refineries_non_eu.log",
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


rule unzip:
    message:
        "Unzipping {wildcards.file}."
    input:
        zip_file="resources/automatic/{file}.zip"
    output:
        file_dir=directory("resources/automatic/{file}/")
    wildcard_constraints:
        file="|".join({"eurostat", "jrc_idees"}),
    log:
        "logs/automatic/unzip_{file}.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/unzip.py"
