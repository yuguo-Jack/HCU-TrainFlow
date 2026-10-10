#!/bin/bash
# ============================================================================
#  /cfs/env.sh — 荣耀训练环境通用配置（容器内 source 或执行）
#
#  用法:
#    source /cfs/env.sh        # 只 export 环境变量（推荐，每次进容器先 source）
#    source /cfs/env.sh apt    # export 环境变量 + 换 apt 源（首次初始化用）
#    bash /cfs/env.sh          # 同上，export 环境变量 + 换 apt 源
#
#  说明: NCCL/RCCL 参数针对海光 HCU(DCU) + dtk26.04 + RoCE(bond0~bond3, mlx5) 调优。
#        eth0 为管理网(10.32.4.x/24)，RoCE 走 NCCL_IB_* 参数。
# ============================================================================

# ---------------------------- NCCL / RCCL settings ----------------------------
export NCCL_SOCKET_IFNAME=eth0
export NCCL_IB_GID_INDEX=3
export NCCL_IB_DISABLE=0
export NCCL_NET_GDR_LEVEL=2
export NCCL_IB_QPS_PER_CONNECTION=4
export NCCL_IB_TC=160
export NCCL_IB_TIMEOUT=22
export GLOO_SOCKET_IFNAME=eth0

# NCCL 拓扑/图文件：存在才加载，不存在用 NCCL 默认值（te 镜像未内置 fix_topo.xml）
#export NCCL_GRAPH_FILE=/opt/dtk/rccl/patch/fix_graph.xml
[[ -f /opt/dtk/rccl/patch/fix_topo.xml ]] && export NCCL_TOPO_FILE=/opt/dtk/rccl/patch/fix_topo.xml
[[ -f /opt/dtk/rccl/patch/fix_graph.xml ]] && export NCCL_GRAPH_FILE=/opt/dtk/rccl/patch/fix_graph.xml
export NCCL_ROCE_SRC_PORT_LIST=60000,60051,57663,57804
export RCCL_MODEL_MATCHING_DISABLE=1
export HSA_FORCE_FINE_GRAIN_PCIE=1
export NCCL_PXN_DISABLE=1
export NCCL_ALGO=Ring

# ---------------------------- pip / uv mirror --------------------------------
export PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple
export PIP_TRUSTED_HOST=mirrors.cloud.tencent.com

# uv config: Tencent PyPI mirror + gh-proxy for python-build-standalone downloads
export UV_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple
export UV_PYTHON_INSTALL_MIRROR="https://gh-proxy.com/github.com/indygreg/python-build-standalone/releases/download"

# ---------------------------- apt 换源（仅直接执行时生效）---------------------
# source 时跳过；bash 执行时换源。
_setup_apt_source() {
    local UBUNTU_VERSION
    UBUNTU_VERSION=$(grep 'VERSION_ID' /etc/os-release | cut -d '=' -f2 | tr -d '"')
    echo "Ubuntu version detected: $UBUNTU_VERSION"
    if [ "$UBUNTU_VERSION" = "22.04" ]; then
        printf '%s\n' \
            'deb http://mirrors.tencent.com/ubuntu/ jammy main restricted universe multiverse' \
            'deb http://mirrors.tencent.com/ubuntu/ jammy-updates main restricted universe multiverse' \
            'deb http://mirrors.tencent.com/ubuntu/ jammy-backports main restricted universe multiverse' \
            'deb http://mirrors.tencent.com/ubuntu/ jammy-security main restricted universe multiverse' \
            > /etc/apt/sources.list
        echo "✅ apt 源已切换为腾讯 jammy 镜像"
    elif [ "$UBUNTU_VERSION" = "24.04" ]; then
        wget -O /etc/apt/sources.list.d/ubuntu.sources https://haihub-model-1251001002.cos.accelerate.myqcloud.com/TCCL/sources_2404.list
        echo "✅ apt 源已切换为腾讯 noble(24.04) 镜像"
    else
        echo "❌ Unsupported Ubuntu version: $UBUNTU_VERSION" >&2
        return 1
    fi
}

# 触发换源的条件：① 直接执行(bash /cfs/env.sh) ② source 时传 "apt" 参数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]] || [[ "${1:-}" == "apt" ]]; then
    _setup_apt_source
fi
