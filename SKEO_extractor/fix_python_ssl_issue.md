The error you're encountering is due to SSL certificate verification failing when a package like `easyocr` tries to download its necessary model files over HTTPS. This is a common issue, especially on macOS systems, when the Python installation doesn't have access to the proper SSL root certificates.

Here's how you can fix this issue:

### **1. Run the `Install Certificates.command` Script**

When you install Python on macOS from the official [python.org](https://www.python.org/) installers, it includes a script to install or update the SSL certificates. This script is typically located in the `/Applications/Python 3.x/` directory.

**Steps:**

1. **Open Terminal.**

2. **Run the following command to execute the script:**

   ```bash
   /Applications/Python\ 3.12/Install\ Certificates.command
   ```

   *Note: Adjust `3.12` to match your installed Python version if it's different.*

   This script will install the necessary SSL certificates for your Python installation.

**Explanation:**

- The script updates your Python's certificate store to use the system's root certificates.
- This allows Python's SSL modules to verify SSL certificates properly.

### **2. Update the `certifi` Package**

If running the script doesn't resolve the issue, ensure that the `certifi` package (which provides Mozilla's CA Bundle) is up to date.

**Steps:**

1. **Run the following command to upgrade `certifi`:**

   ```bash
   pip install --upgrade certifi
   ```

2. **Verify the installation by running:**

   ```bash
   python -c "import certifi; print(certifi.where())"
   ```

   This should display the path to the `certifi` CA bundle.

### **3. Modify `easyocr` to Use `certifi`'s SSL Context (Advanced)**

If the issue persists after attempting the above steps, you can modify `easyocr` to use `certifi`'s SSL context when downloading models. This involves editing the library code, which isn't recommended for long-term solutions but can help in this specific case.

**Steps:**

1. **Locate the `utils.py` file in the `easyocr` package.**

   The file is typically located at:

   ```
   <path_to_python_site_packages>/easyocr/utils.py
   ```

2. **Modify the `download_and_unzip` function:**

   Add the following code at the beginning of the `download_and_unzip` function:

   ```python
   import ssl
   import certifi
   import urllib.request

   def download_and_unzip(url, filename, model_storage_directory, verbose=True):
       # Add these lines to set up SSL context with certifi
       ssl_context = ssl.create_default_context(cafile=certifi.where())
       opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context))
       urllib.request.install_opener(opener)
       # Rest of your function continues...
   ```

3. **Save the changes and retry running your script.**

**Note:** Modifying library code is not generally recommended because:

- Updates to the library may overwrite your changes.
- Other parts of the code may expect the original behavior.

### **Alternate Workaround (Not Recommended)**

As a temporary measure, you can disable SSL verification. **However, this is insecure and should not be used in production environments.**

**Steps:**

1. **Add the following code before your script imports:**

   ```python
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
   ```

2. **Run your script.**

This tells Python to ignore SSL certificate verification, which can help in cases where SSL certificates cannot be verified but is a significant security risk.

**Note:** This method is not recommended due to the security implications.

### **Recommendation**

The recommended and secure solution is to run the `Install Certificates.command` script provided by your Python installation. This should resolve SSL certificate verification issues across all Python modules without needing to modify library code or disable SSL verification.

### **Next Steps**

1. **Run the `Install Certificates.command` script.**

2. **Retry running your script:**

   ```bash
   python skeo.py --pdf-dir ./ --output-dir ./
   ```

3. **If the issue persists, ensure that `certifi` is up to date.**

4. **Avoid disabling SSL verification unless absolutely necessary and you're aware of the security risks.**

By following these steps, you should be able to resolve the SSL certificate verification error and proceed with processing your PDF files.