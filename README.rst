Lemur (Spotify fork)
====================

.. note::

   This is Spotify's maintained fork of `Netflix/lemur <https://github.com/Netflix/lemur>`_,
   which was archived on July 6, 2026.

   We use Lemur internally for TLS certificate lifecycle management across our
   edge infrastructure. This fork contains bug fixes and operational improvements
   specific to our deployment. Community contributions are welcome.

   The original Spotify fork (``master`` branch, pre-Netflix sync) is preserved
   as the ``old_fork`` branch for reference.


Lemur manages TLS certificate creation. While not able to issue certificates itself, Lemur acts as a broker between CAs
and environments providing a central portal for developers to issue TLS certificates with 'sane' defaults.


Project resources
=================

- `Original Netflix Blog Post <http://techblog.netflix.com/2015/09/introducing-lemur.html>`_
- `Documentation <http://lemur.readthedocs.io/>`_
- `Upstream source (archived) <https://github.com/Netflix/lemur>`_
- `Issue tracker <https://github.com/spotify/lemur/issues>`_
