import math

# ==========================
# OFDMA BW 換算
# ==========================
def ofdma_convert(power_dbmv, source_bw, target_bw):

    if source_bw <= 0 or target_bw <= 0:
        return 0

    return power_dbmv + 10 * math.log10(
        target_bw / source_bw
    )


# ==========================
# SC-QAM Total Power
# ==========================
def scqam_total_power(power_list):

    if len(power_list) == 0:
        return 0

    linear_sum = sum(
        10 ** (p / 10)
        for p in power_list
    )

    return 10 * math.log10(linear_sum)


# ==========================
# OFDMA Multiple Blocks
# ==========================
def ofdma_multi_total(blocks):

    """
    blocks:
    [
      {"power":41.0,"bw":96},
      {"power":42.0,"bw":192}
    ]
    """

    psd_linear = 0

    for blk in blocks:

        p = blk["power"]
        bw = blk["bw"]

        psd_linear += (
            10 ** (
                (p - 10 * math.log10(bw))
                / 10
            )
        )

    total_bw = sum(
        blk["bw"]
        for blk in blocks
    )

    return (
        10 * math.log10(
            psd_linear * total_bw
        )
    )


# ==========================
# Mixed OFDMA + SCQAM
# ==========================
def mixed_total_power(
        ofdma_blocks,
        scqam_channels):

    total_linear = 0

    # OFDMA
    for blk in ofdma_blocks:

        total_linear += (
            10 ** (
                blk["power"] / 10
            )
        )

    # SCQAM
    for p in scqam_channels:

        total_linear += (
            10 ** (p / 10)
        )

    return (
        10 * math.log10(
            total_linear
        )
    )
