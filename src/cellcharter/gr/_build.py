from __future__ import annotations

import numpy as np
from anndata import AnnData
from scipy.sparse import csr_matrix
from squidpy._constants._constants import CoordType, Transform
from squidpy._constants._pkg_constants import Key
from squidpy._docs import d, inject_docs
from squidpy.gr._utils import _assert_connectivity_key


@d.dedent
@inject_docs(t=Transform, c=CoordType)
def remove_long_links(
    adata: AnnData,
    distance_percentile: float = 99.0,
    connectivity_key: str | None = None,
    distances_key: str | None = None,
    copy: bool = False,
) -> tuple[csr_matrix, csr_matrix] | None:
    """
    Create a graph from spatial coordinates using a modified version of Squidpy's function gr.spatial_neighbors.

    It implements an automatic procedure to remove links between cells at a distance bigger than a certain percentile of all positive distances.
    It is designed for data with generic coordinates.

    Parameters
    ----------
    %(adata)s

    distance_percentile
        Percentile of the distances between cells over which links are trimmed after the network is built.
    %(conn_key)s

    distances_key
        Key in :attr:`anndata.AnnData.obsp` where spatial distances are stored.
        Default is: :attr:`anndata.AnnData.obsp` ``['{{Key.obsp.spatial_dist()}}']``.

    %(copy)s

    Returns
    -------
    If ``copy = True``, returns a :class:`tuple` with the new spatial connectivities and distances matrices.

    Otherwise, modifies the ``adata`` with the following keys:
        - :attr:`anndata.AnnData.obsp` ``['{{key_added}}_connectivities']`` - the spatial connectivities.
        - :attr:`anndata.AnnData.obsp` ``['{{key_added}}_distances']`` - the spatial distances.
        - :attr:`anndata.AnnData.uns`  ``['{{key_added}}']`` - :class:`dict` containing parameters.
    """
    connectivity_key = Key.obsp.spatial_conn(connectivity_key)
    distances_key = Key.obsp.spatial_dist(distances_key)
    _assert_connectivity_key(adata, connectivity_key)
    _assert_connectivity_key(adata, distances_key)

    conns, dists = adata.obsp[connectivity_key], adata.obsp[distances_key]

    if copy:
        conns, dists = conns.copy(), dists.copy()

    threshold = np.percentile(np.array(dists[dists != 0]).squeeze(), distance_percentile)
    conns[dists > threshold] = 0
    dists[dists > threshold] = 0

    conns.eliminate_zeros()
    dists.eliminate_zeros()

    if copy:
        return conns, dists
