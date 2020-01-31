=======
Filters
=======

The ``cosmic-ray init`` commands scans a module for all possible mutations, but we don't always want to execute all of
these. For example, we may know that some of these mutations will result in *equivalent mutants*, so we need a way to
prevent these mutations from actually being run.

To account for this, Cosmic Ray includes a number of *filters*. Filters are nothing more than programs - generally small
ones - that modify a session in some way, often by marking certains mutations as "skipped", thereby preventing them from
running. The name "filter" is actually a bit misleading since these programs could modify a session in ways other than
simply skipping some mutations. In practice, though, the need to skip certain tests is by far the most common use of
these programs.

.. note::

  Filter are what used to be called *interceptors*. Interceptors were more tightly integrated with the ``init`` command,
  with many of the problems that unnecessarily high coupling often brings with it. Filters are simpler and more flexible than
  interceptors with no loss in power.

Filters included with Cosmic Ray
================================

Cosmic Ray comes with a number of filters. Remember, though, that they are nothing more than simple programs that modify
a session in some way; it should be straightforward to write your own filters should the need arise.

cr-filter-spor
--------------

The ``cr-filter-spor`` filter modifies a session by skipping mutations which are indicated in a `spor
<https://github.com/abingham/rust_spor>`_ anchored metadata repository. In short, `spor` provides a way to associated
arbitrary metadata with ranges of code, and this metadata is stored outside of the code. As your code changes, ``spor``
has algorithms to update the metadata (and its association with the code) automatically.


This filter looks for anchors containing the metadata ``mutate: False``. Any code anchored with this metadata will not
be mutated in any way by Cosmic Ray.

See ``spor``'s documentation for more information on how to create and manage anchors.

cr-filter-operators
-------------------

``cr-filter-operators`` allows you to filter out operators according to their names. You provide the filter with a set
of regular expressions, and any Cosmic Ray operator who's name matches a one of these expressions will be skipped
entirely.

The configuration is provided through a TOML file such as a standard Cosmic Ray configuration. The expressions must be
in a list at the key "cosmic-ray.operators-filter.exclude-operators". Here's an example::

  [cosmic-ray.operators-filter]
  exclude-operators = [
    "core/ReplaceComparisonOperator_Is(Not)?_(Not)?(Eq|[LG]tE?)",
    "core/ReplaceComparisonOperator_(Not)?(Eq|[LG]tE?)_Is(Not)?",
    "core/ReplaceComparisonOperator_[LG]tE_Eq",
    "core/ReplaceComparisonOperator_[LG]t_NotEq",
  ]

For a list of all operators in your Cosmic Ray installation, run ``cosmic-ray operators``.

cr-filter-pragma
----------------

The ``cr-filter-pragma`` filter looks for lines in your source code containing the comment "# pragma: no mutate". Any
mutation in a session that would mutate such a line is skipped.

cr-filter-git
-------------

The ``cr-filter-git`` filter looks for edited or new lines from the given git branch. Any mutation in a session that
would mutate other lines is skipped.

By default the ``master`` branch is used, but you could define another one like this:

  [cosmic-ray.git-filter]
  branch = "rolling"

Using filters
=============

Generally speaking, filters will be run immediately after running ``cosmic-ray init``. It's up to you to decide which to
run, and often they will be run along with ``init`` in a batch script or CI configuration.

For example, if you wanted to apply the ``cr-filter-pragma`` filter to your session, you could do something like this::

  cosmic-ray init cr.conf session.sqlite
  cr-filter-pragma session.sqlite

The ``init`` would first create a session where *all* mutation would be run, and then the ``cr-filter-pragma`` call
would mark as skipped all mutations which are on a line with the pragma comment.
