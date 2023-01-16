# ArXiVFetcher

Simple script to find articles from ArXiv based on a set of keywords and categories

## Instalation 

Just make sure to install all the requirements from `requirements.txt` by using

```
python -r requirements.txt
```

Tested using python 3.9+

## Basic usage 

Use the `input.yaml` file to input the categories and keywords to search. 
To run the file

```
python ArXivFetcher.py -inp=input.yaml -f='Articles'
```

where an the name of the yaml input file and the name used for the outputfiles is given. It creates a `.bib`file and and `.xlsx`file with all files found.

To see all the possible arguments use  

```
python ArXivFetcher.py --help
```

### Run at startup

It can be usefull to run the script automatically at the startup of the computer. The simplest way to do it in linux systems is by using **cron**. For this specific case the *crontab* file must be edited: 

```
$ crontab -e
```

To run the script at startup this line must be added: 

```
@reboot python /path/to/ArXivFetcher.py -i your_input_file.yaml -f 'Your_File_Name'
``` 