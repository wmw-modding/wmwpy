# wmwpy
 Python module for working with Where's My...? game files.

 <!-- Note: using https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/ for distributing.-->

 This is going to be used in Where's My Editor, a level editor for the Where's My...? series.

# Building package
 To build the package, install `build`
 ```
pip install build
 ```
 Then run
 ```
py -m build
 ```

# Building docs
 To build the docs, make sure sphinx is installed
 ```
pip install -U sphinx
 ```

 You then need to run
 ```
sphinx-build -b html doc-build docs
 ```

# Credits
- Thanks to [@campbellsonic](https://github.com/campbellsonic) for the script to read waltex images. I could not have done it without them.
- Thanks to [Mark Setchell](https://stackoverflow.com/a/75511423/17129659) for helping to make loading waltex images faster (still need rgb565 and rgba5551).
