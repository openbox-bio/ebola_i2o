
<img src="https://github.com/openbox-bio/assets/blob/master/openboxbio_logo.png" width="250" height="60">

### Welcome to the ebola_i2o Pipeline Repo.

#### Introduction
The ebola_i2o pipeline has been built to process the output from the EBOV chip, designed by the Duncan Lab, at the Center For Biologics Evaluation and Research ([CBER](https://www.fda.gov/about-fda/fda-organization/center-biologics-evaluation-and-research-cber)), FDA.
EBOV has been designed to type strains of the Ebola virus using a Multi-Locus Subtyping (MLST) strategy.
Briefly, the chip generates sequence from 13 regions of the Ebola virus genome sequence. Generated sequences are aligned with the corresponding regions from 149 reference Ebola strains with know strain type. A phylogenetic tree derived from the concatenated alignment, across the 13 segments, allows one to establish the evolutionary relationships between the test strain and the reference strains.

#### Requirements
To run this pipeline you will need to install:
1. [Git](https://github.com/git-guides/install-git) and [Docker](https://docs.docker.com/get-docker/)
2. the following Perl modules:
    * File::Path
    * File::SortedSeek
    * hint: `sudo perl -MCPAN -e 'install <module_name>'`
3. the following:
   * a Blast database. You can use the nt database from NCBI. Alternatively you can create your own database of Filovirus nucleotide sequences, using code included in this repo (see below).
   * The nucl_gb.accession2taxid.gz from `ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz`. Be sure to unzip file before use.
   * The names.dmp file from the taxdump.tar.gz file-set at `ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz`. Be sure to unzip file before use.

#### Usage
1. Clone this repo to your local machine: `git clone https://github.com/openbox-bio/ebola_i2o.git`.
2. The `ebola_i2o` directory has the following subdirectories:
<br>_ebola_i2o_
<br>|-->_code_ (stores the ebola_i2o code and ebola_i2o settings file. Stores the program create_blast_nucl_database.py and an associated environment file, filovirus_env, to create and maintain a Filovirus database.)
<br>|-->_data_ (stores all reference strain multiple sequence alignments)

3. Configure the path variables in file ebola_i2o_settngs file. This settings file stores the path to a set of key files and directories for ebola_i2o.
  * REF_DATA_PATH: Path to the data sub-directory in the ebola_i2o directory.
  * BLAST_DB_PATH: Path to the directory storing the Blast database.
  * BLAST_DB_NAME: Name of the Blast database.
  * ACC2TAXID_PATH: Path to the nucl.gb.accession2taxid file.
  * NAMES_DMP_PATH: Path to the names.dmp file.
  * RESULTS_PATH: Path to the folder that stores output from ebola_i2o. For each sample that is run, the pipeline creates a subfolder
      (name format = <Sample_Name>\_YYYY_MM_DD_HH_MM_SS) here to store all the output files.
4. Pull the following docker image `openboxbio/ebola_i2o_tools:latest`
    * hint: `docker pull openboxbio/ebola_i2o_tools:latest`

5. Set environmental variable `CODE_PATH` to the absolute path to the `ebola_i2o_settings` file. In Ubuntu this can be done by adding `export CODE_PATH=<path_to_ebola_i2o_settings_file>` in the .profile file.

6. Run the pipeline: `perl ebola_i2o <full_path_name_to_input_file>`

Important:
1. Path names should have no spaces in them. Good folder name: `data_folder`. Bad folder name: `data folder`.
2. Please ensure that the name of the input file is of the following format: <test_strain_name>.txt, where test_strain_name is **no longer than ten characters**.
3. **Disclaimer:** This pipeline has been tested on Ubnutu. It should, in principle, work on all flavors of Unix. Please mail me at anjan.purkayastha@gmail.com to report problems or bugs.

#### Setting up a Filovirus database
1. Ensure that the following Python packages are installed in your environment: `biopython`, `python-dotenv`, `pathlib`
2. In your BlAST database folder create a file, that will serve as the log file for the program.
  * hint: `touch filoviridae.db.log`
3. Open the environment file ebola_env in a text editor, specify the absolute path of the filovirus database using the `DB` environment variable; specify the path of the log file created in step 2, using the `LOG` environment variable. Please do not alter any of the other variables.
4. To create a Filovirus database run `python <path_to_create_blast_nucl_database.py> -e <path_to_filovirus_env> -t create`
