Time Split
==========
Time-based k-fold validation splits for heterogeneous data.

Experimenting with parameters
-----------------------------
The **Time Fold Explorer** application
(available `here <https://time-split.streamlit.app/?data=1554942900-1557610200&schedule=0+0+%2A+%2A+MON%2CFRI&n_splits=2&step=2&show_removed=True>`_)
is designed to help evaluate the effects of different
:ref:`parameters <Parameter overview>`.
To start it locally using
|shield-0|
Docker, run

.. code-block::

    docker run -p 8501:8501 rsundqvist/time-split

in the terminal. You may use
:func:`~time_split.app.create_explorer_link`
to build application URLs with preselected splitting parameters.


.. |shield-0| image:: https://img.shields.io/docker/image-size/rsundqvist/time-split/latest?logo=docker&label=time-split
                  :target: https://hub.docker.com/r/rsundqvist/time-split/
                  :alt: Docker Image Size (tag)

.. include:: guide/parameters.rst

.. toctree::
   :hidden:

   API reference <api/time_split>
   auto_examples/index
   guide/index
   development
   changelog/index

Shortcuts
---------
Click an image below to get started, or use the top navigation bar.
