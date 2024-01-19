# HuggingFace Analyser

HuggingFace text generation and text classification models and related spaces analyser written in Python.

## Get started
Local:
```
git clone git@github.com:AMK9978/HuggingAnalyser.git
pip install -r requirements.txt
python main.py
```
Docker:
```
git clone git@github.com:AMK9978/HuggingAnalyser.git
docker build hugging .
docker run --name hugging -itd hugging
```

## Comparison and Results

[Comparison.md](Comparison.md)

## File Structure

- datasets: The obtained datasets from crawling used in the analysis
- media: The drawn figures by draw.py used in the analysis
- tests: The test file of the project containing four tests
- main.py: The main file of the project containing the crawler
- drawer.py: The helper module for drawing the figures

## Authors

- Amir Karimi [AMK9978](https://github.com/amk9978)

## Built With

- Python 3.11
- requests
- BeautifulSoup4
- pandas
- matplotlib
- Black
- isort

Due to the above requirements, the application is blazing fast and lightweight.
It does not use any browser instance. No captcha test was recorded during crawling.

## License

This project is licensed under the MIT License.

## Discussion on HuggingFace

There is an open thread on HuggingFace opened by Amir Karimi requesting the app size feature from HuggingFace Hub API:

[Thread](https://discuss.huggingface.co/t/space-app-size-calculation/69588)
