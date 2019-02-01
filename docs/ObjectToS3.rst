.. image:: images/LOGOS.png

================
Object To AWS S3
================

The following is the complete ``obj_to_s3.py``. It does the following:

- Checks if there exists a file with the same name currently in the S3 Bucket.
- [If yes] deletes the file in the Bucket
- Uploads local file to S3 as a publically readable file.

.. literalinclude:: C:\Users\Hail\Desktop\Github\RealTimeRecs-gregjewi\obj_to_s3.py

