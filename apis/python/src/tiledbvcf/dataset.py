import pandas as pd
import sys
import warnings

from collections import namedtuple
from . import libtiledbvcf

ReadConfig = namedtuple(
    "ReadConfig",
    [
        # Max number of records (rows) to read.
        "limit",
        # Region partition tuple (idx, num_partitions)
        "region_partition",
        # Samples partition tuple (idx, num_partitions)
        "sample_partition",
        # Whether or not to sort the regions to be read (default True)
        "sort_regions",
        # Memory budget (MB) for buffer and internal allocations (default 2048MB)
        "memory_budget_mb",
        # List of strings of format 'option=value'
        "tiledb_config",
    ],
)
ReadConfig.__new__.__defaults__ = (None,) * 6  # len(ReadConfig._fields)


class Dataset(object):
    """A handle on a TileDB-VCF dataset."""

    def __init__(self, uri, mode="r", cfg=None, stats=False, verbose=False):
        """Initializes a TileDB-VCF dataset for interaction.

        :param uri: URI of TileDB-VCF dataset
        :param mode: Mode of operation.
        :type mode: 'r' or 'w'
        :param cfg: TileDB VCF configuration (optional)
        :param stats: Enable or disable TileDB stats (optional)
        :param verbose: Enable or disable TileDB VCF verbose output (optional)
        """
        self.uri = uri
        self.mode = mode
        self.cfg = cfg
        if self.mode == "r":
            self.reader = libtiledbvcf.Reader()
            self._set_read_cfg(cfg)
            self.reader.init(uri)
            self.reader.set_tiledb_stats_enabled(stats)
            self.reader.set_verbose(verbose)
        elif self.mode == "w":
            self.writer = libtiledbvcf.Writer()
            self._set_write_cfg(cfg)
            self.writer.init(uri)
            self.writer.set_verbose(verbose)
        else:
            raise Exception("Unsupported dataset mode {}".format(mode))

    def _set_read_cfg(self, cfg):
        if cfg is None:
            return
        if cfg.limit is not None:
            self.reader.set_max_num_records(cfg.limit)
        if cfg.region_partition is not None:
            self.reader.set_region_partition(*cfg.region_partition)
        if cfg.sample_partition is not None:
            self.reader.set_sample_partition(*cfg.sample_partition)
        if cfg.sort_regions is not None:
            self.reader.set_sort_regions(cfg.sort_regions)
        if cfg.memory_budget_mb is not None:
            self.reader.set_memory_budget(cfg.memory_budget_mb)
        if cfg.tiledb_config is not None:
            tiledb_config_list = list()
            if isinstance(cfg.tiledb_config, list):
                tiledb_config_list = cfg.tiledb_config
            # Support dictionaries and tiledb.Config objects also
            elif isinstance(cfg.tiledb_config, dict):
                for key in cfg.tiledb_config:
                    if cfg.tiledb_config[key] != "":
                        tiledb_config_list.append(
                            "{}={}".format(key, cfg.tiledb_config[key])
                        )
            else:
                try:
                    import tiledb

                    if isinstance(cfg.tiledb_config, tiledb.Config):
                        for key in cfg.tiledb_config:
                            if cfg.tiledb_config[key] != "":
                                tiledb_config_list.append(
                                    "{}={}".format(key, cfg.tiledb_config[key])
                                )
                except ImportError:
                    pass
            self.reader.set_tiledb_config(",".join(tiledb_config_list))

    def _set_write_cfg(self, cfg):
        if cfg is None:
            return
        if cfg.tiledb_config is not None:
            tiledb_config_list = list()
            if isinstance(cfg.tiledb_config, list):
                tiledb_config_list = cfg.tiledb_config
            # Support dictionaries and tiledb.Config objects also
            elif isinstance(cfg.tiledb_config, dict):
                for key in cfg.tiledb_config:
                    if cfg.tiledb_config[key] != "":
                        tiledb_config_list.append(
                            "{}={}".format(key, cfg.tiledb_config[key])
                        )
            else:
                try:
                    import tiledb

                    if isinstance(cfg.tiledb_config, tiledb.Config):
                        for key in cfg.tiledb_config:
                            if cfg.tiledb_config[key] != "":
                                tiledb_config_list.append(
                                    "{}={}".format(key, cfg.tiledb_config[key])
                                )
                except ImportError:
                    pass
            self.writer.set_tiledb_config(",".join(tiledb_config_list))

    def read(self, attrs, samples=None, regions=None, samples_file=None, bed_file=None):

        """Reads data from a TileDB-VCF dataset.

        For large datasets, a call to `read()` may not be able to fit all
        results in memory. In that case, the returned dataframe will contain as
        many results as possible, and in order to retrieve the rest of the
        results, use the `continue_read()` function.

        You can also use the Python generator version, `read_iter()`.

        :param list of str attrs: List of attribute names to be read.
        :param list of str samples: CSV list of sample names to be read.
        :param list of str regions: CSV list of genomic regions to be read.
        :param str samples_file: URI of file containing sample names to be read,
            one per line.
        :param str bed_file: URI of a BED file of genomic regions to be read.
        :return: Pandas DataFrame containing results.
        """
        if self.mode != "r":
            raise Exception("Dataset not open in read mode")

        self.reader.reset()
        self._set_samples(samples, samples_file)

        regions = "" if regions is None else regions
        self.reader.set_regions(",".join(regions))
        self.reader.set_attributes(attrs)

        if bed_file is not None:
            self.reader.set_bed_file(bed_file)

        return self.continue_read()

    def read_iter(
        self, attrs, samples=None, regions=None, samples_file=None, bed_file=None
    ):
        if self.mode != "r":
            raise Exception("Dataset not open in read mode")

        if not self.read_completed():
            yield self.read(attrs, samples, regions, samples_file, bed_file)
        while not self.read_completed():
            yield self.continue_read()

    def continue_read(self):
        if self.mode != "r":
            raise Exception("Dataset not open in read mode")

        self.reader.read()
        table = self.reader.get_results_arrow()
        return table.to_pandas()

    def read_completed(self):
        """Returns true if the previous read operation was complete.

        A read is considered complete if the resulting dataframe contained
        all results."""
        if self.mode != "r":
            raise Exception("Dataset not open in read mode")
        return self.reader.completed()

    def count(self, samples=None, regions=None):
        """Counts data in a TileDB-VCF dataset.

        :param list of str samples: CSV list of sample names to include in
            the count.
        :param list of str regions: CSV list of genomic regions include in
            the count
        :return: Number of intersecting records in the dataset
        """
        if self.mode != "r":
            raise Exception("Dataset not open in read mode")
        self.reader.reset()

        samples = "" if samples is None else samples
        regions = "" if regions is None else regions
        self.reader.set_samples(",".join(samples))
        self.reader.set_regions(",".join(regions))

        self.reader.read()
        if not self.read_completed():
            raise Exception("Unexpected read status during count.")

        return self.reader.result_num_records()

    def create_dataset(
        self,
        extra_attrs=None,
        tile_capacity=None,
        anchor_gap=None,
        checksum_type=None,
        allow_duplicates=True,
    ):
        """Create a new dataset

        :param list of str extra_attrs: CSV list of extra attributes to
            materialize from fmt field
        :param int tile_capacity: Tile capacity to use for the array schema
            (default = 10000).
        :param int anchor_gap: Length of gaps between inserted anchor records in
            bases (default = 1000).
        :param str checksum_type: Optional override checksum type for creating
            new dataset valid values are sha256, md5 or none.
        :param bool allow_duplicates: Allow records with duplicate start
            positions to be written to the array.
        """
        if self.mode != "w":
            raise Exception("Dataset not open in write mode")

        extra_attrs = "" if extra_attrs is None else extra_attrs
        self.writer.set_extra_attributes(",".join(extra_attrs))

        if tile_capacity is not None:
            self.writer.set_tile_capacity(tile_capacity)

        if anchor_gap is not None:
            self.writer.set_anchor_gap(anchor_gap)

        if checksum_type is not None:
            checksum_type = checksum_type.lower()
            self.writer.set_checksum(checksum_type)

        self.writer.set_allow_duplicates(allow_duplicates)

        # Create is a no-op if the dataset already exists.
        # TODO: Inform user if dataset already exists?
        self.writer.create_dataset()

    def ingest_samples(
        self,
        sample_uris=None,
        threads=None,
        memory_budget=None,
        scratch_space_path=None,
        scratch_space_size=None,
        sample_batch_size=None,
    ):
        """Ingest samples

        :param list of str sample_uris: CSV list of sample names to include in
            the count.
        :param int threads: Set the number of threads used for ingestion.
        :param int memory_budget: Set the max size (MB) of TileDB buffers before flushing
            (default = 1024).
        :param str scratch_space_path: Directory used for local storage of
            downloaded remote samples.
        :param int scratch_space_size: Amount of local storage that can be used
            for downloading remote samples (MB).
        """

        if self.mode != "w":
            raise Exception("Dataset not open in write mode")

        if sample_uris is None:
            return

        if threads is not None:
            self.writer.set_num_threads(threads)

        if memory_budget is not None:
            self.writer.set_memory_budget(memory_budget)

        if scratch_space_path is not None and scratch_space_size is not None:
            self.writer.set_scratch_space(scratch_space_path, scratch_space_size)
        elif scratch_space_path is not None or scratch_space_size is not None:
            raise Exception(
                "Must set both scratch_space_path and scratch_space_size to use scratch space"
            )

        if sample_batch_size is not None:
            self.writer.set_sample_batch_size(sample_batch_size)

        self.writer.set_samples(",".join(sample_uris))

        # Only v2 and v3 datasets need registration
        if self.schema_version() < 4:
            self.writer.register_samples()
        self.writer.ingest_samples()

    def tiledb_stats(self):
        if self.mode != "r":
            raise Exception("Stats can only be called for reader")

        if not self.reader.get_tiledb_stats_enabled:
            raise Exception("Stats not enabled")

        return self.reader.get_tiledb_stats()

    def schema_version(self):
        """Retrieve the VCF dataset's schema version"""
        if self.mode != "r":
            return self.writer.get_schema_version()
        return self.reader.get_schema_version()

    def sample_count(self):
        if self.mode != "r":
            raise Exception("Samples can only be retrieved for reader")
        return self.reader.get_sample_count()

    def samples(self):
        """Retrieve list of sample names registered in the VCF dataset"""
        if self.mode != "r":
            raise Exception("Sample names can only be retrieved for reader")
        return self.reader.get_sample_names()

    def attributes(self, attr_type="all"):
        """List queryable attributes available in the VCF dataset

        :param str type: The subset of attributes to retrieve; "info" or "fmt"
            will only retrieve attributes ingested from the VCF INFO and FORMAT
            fields, respectively, "builtin" retrieves the static attributes
            defiend in TileDB-VCF's schema, "all" (the default) returns all
            queryable attributes
        :returns: a list of strings representing the attribute names
        """

        if self.mode != "r":
            raise Exception("Attributes can only be retrieved in read mode")

        attr_types = ("all", "info", "fmt", "builtin")
        if attr_type not in attr_types:
            raise ValueError("Invalid attribute type. Must be one of: %s" % attr_types)

        # combined attributes with type object
        comb_attrs = ("info", "fmt")

        if attr_type == "info":
            return self._info_attrs()
        elif attr_type == "fmt":
            return self._fmt_attrs()
        else:
            attrs = set(self._queryable_attrs()).difference(comb_attrs)
            if attr_type == "builtin":
                attrs.difference_update(self._info_attrs() + self._fmt_attrs())
            return sorted(list(attrs))

    def _queryable_attrs(self):
        return self.reader.get_queryable_attributes()

    def _fmt_attrs(self):
        return self.reader.get_fmt_attributes()

    def _info_attrs(self):
        return self.reader.get_info_attributes()

    def _set_samples(self, samples=None, samples_file=None):
        if samples is not None and samples_file is not None:
            raise TypeError(
                "Argument 'samples' not allowed with 'samples_file'. "
                "Only one of these two arguments can be passed at a time."
            )
        elif samples is not None:
            self.reader.set_samples(",".join(samples))
        elif samples_file is not None:
            self.reader.set_samples("")
            self.reader.set_samples_file(samples_file)


class TileDBVCFDataset(Dataset):
    """A handle on a TileDB-VCF dataset."""

    def __init__(self, uri, mode="r", cfg=None, stats=False, verbose=False):
        """Initializes a TileDB-VCF dataset for interaction.

        :param uri: URI of TileDB-VCF dataset
        :param mode: Mode of operation.
        :type mode: 'r' or 'w'
        :param cfg: TileDB VCF configuration (optional)
        :param stats: Enable or disable TileDB stats (optional)
        :param verbose: Enable or disable TileDB VCF verbose output (optional)
        """
        warnings.warn(
            "TileDBVCFDataset is deprecated, use Dataset instead", DeprecationWarning
        )
        super().__init__(uri, mode, cfg, stats, verbose)
