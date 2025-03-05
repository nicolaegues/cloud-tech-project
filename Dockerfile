# base on latest python image
FROM python:latest

# add our python program
ADD hzz_analysis.py requirements.txt infofile.py ./

# install dependent libraries
RUN pip install -r requirements.txt

# the command to run our program
CMD ["python", "./hzz_analysis.py"]


