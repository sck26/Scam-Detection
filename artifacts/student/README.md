# Distilled on-device student

The full text-to-probability model is `student.onnx`. It contains word TF-IDF
(1-2 grams) plus a logistic-regression classifier. `student.joblib` is the exact
scikit-learn source pipeline, and `preprocessing.json` contains the 1,650-feature
vocabulary, IDF weights, and linear-head parameters for an iOS implementation.

`student-linear.mlmodel` is a Core ML export of the linear head. The app must create
the TF-IDF vector from `preprocessing.json` before invoking it. The complete sklearn
pipeline could not be converted to Core ML because coremltools does not support
`TfidfVectorizer`; the exact error is retained in `metrics.json`. The ONNX artifact
does contain the complete text pipeline and passed an onnxruntime smoke inference.
The Core ML head also passed a native macOS smoke inference; a zero TF-IDF vector
produced scam probability 0.5611003.

## Reproduce on a Mac

1. Install Xcode command-line tools: `xcode-select --install`.
2. From the repository, run `make setup`.
3. Install export extras with `.venv/bin/python -m pip install -e '.[student]'`.
4. Download/process UCI data with `make data`, start Ollama, and pull the teacher
   with `make models`.
5. Run `make distill`. Teacher labels remain ignored under `data/distill/`; exports
   are written here.
6. In iOS, copy `preprocessing.json` and `student-linear.mlmodel` into the Xcode
   target. Reproduce lowercase word unigrams/bigrams, sublinear TF `1 + log(count)`,
   multiply by the matching IDF value, L2-normalize the 1,650-element vector, and
   pass it to the generated Core ML class as `tfidf`.

The Core ML head and ONNX model use float32 with no quantization. At only tens of
kilobytes, quantization would add validation risk with negligible storage benefit.
