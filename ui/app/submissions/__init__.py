"""Submission records and the bytes behind them.

``/submit`` reports each submission to BERIL here, independently of the
context store's indexing: the record (``app.db.models.Submission``), its
manifest, and the wiki-relevant bytes in a :class:`SubmissionStore`.
"""
