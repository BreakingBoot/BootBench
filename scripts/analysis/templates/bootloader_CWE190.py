# Arbiter vulnerability template: integer overflow reaching an allocation or
# copy, targeted at bootloader code.
#
# Two things to know if you write your own:
#
#  * run_arbiter.py calls `template.apply_constraint`, but every template
#    arbiter ships defines `constrain` instead, so the shipped templates fail
#    with AttributeError. This file defines apply_constraint and aliases
#    constrain to it, so it works either way.
#
#  * Those templates also name Juliet test-suite functions (printUnsignedLine,
#    badSource), which appear in no real bootloader. The sinks and sources
#    below are the allocation, copy and input routines that actually occur in
#    UEFI firmware, U-Boot and libc-linked bootloader utilities.
#
# Used by: run-tool.sh arbiter <binary>


def apply_constraint(state, expr, init_val, **kwargs):
    """Flag a size expression that can end up smaller than its inputs, i.e. wrapped."""
    for x in init_val:
        x = x[31:]
        expr = expr[31:]
        if x.length < expr.length:
            x = x.zero_extend(expr.length - x.length)
        state.solver.add(expr < x)


# run_arbiter.py wants apply_constraint; arbiter's own templates use constrain.
constrain = apply_constraint


def specify_sinks():
    """Sink -> tracked argument.

    The name is a role label, not the real parameter name. arbiter's
    Target.sz is hardcoded to `args.index('n')`, so the size argument must be
    called 'n' whatever the function's actual prototype says (angr calls it
    'size' for memcpy, 'eltsize' for calloc, and so on). Likewise 'fmt' for a
    format string and 'i' for the input argument. Using the real names gives
    "ValueError: 'n' is not in list".
    """
    size_sinks = [
        # UEFI boot services and EDK-II memory helpers
        "AllocatePool", "AllocateZeroPool", "AllocatePages", "AllocateCopyPool",
        "CopyMem", "SetMem",
        # U-Boot / barebox
        "malloc_simple", "memalign_simple",
        # libc, for host-side bootloader utilities such as kexec-tools
        "malloc", "calloc", "realloc", "memcpy", "memmove",
        "strncpy", "strncat", "snprintf", "vsnprintf",
    ]
    return {name: ["n"] for name in size_sinks}


def specify_sources():
    """Source -> index of the argument that carries attacker-controlled data.

    A bootloader's untrusted inputs are the things it parses before anything
    has been verified: files and images off disk, network responses, and
    non-volatile variables.
    """
    return {
        # libc input
        "read": 2,
        "fread": 1,
        "recv": 2,
        "fgets": 1,
        "atoi": 0,
        "atol": 0,
        "strtoul": 0,
        "strtol": 0,
        "sscanf": 2,
        "fscanf": 3,
        # UEFI: variables, files and network are all pre-verification input
        "GetVariable": 4,
        "GetNextVariableName": 0,
        "Read": 2,
        "ReadBlocks": 3,
        # U-Boot environment
        "env_get": 0,
        "simple_strtoul": 0,
    }


def save_results(reports):
    import json
    import os

    out = os.environ.get("ARBITER_OUT", ".")
    findings = []
    for r in reports:
        findings.append({
            "bbl": hex(r.bbl),
            "history": [str(x) for x in r.bbl_history],
        })
    with open(os.path.join(out, "findings.json"), "w") as f:
        json.dump(findings, f, indent=2)
    print(f"\n  {len(findings)} finding(s)")
    for f_ in findings:
        print(f"    {f_['bbl']}")
