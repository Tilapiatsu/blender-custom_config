import bpy

from bpy.types import (
    PropertyGroup,
)

from bpy.props import (
    EnumProperty,
    BoolProperty,
    StringProperty,
    IntProperty,
    FloatProperty,
)

class SRF_Settings(PropertyGroup):

    # Show Panels

    show_master: BoolProperty(
        default=True,
    )

    show_master_general: BoolProperty(
        default=True,
    )

    show_master_advanced: BoolProperty(
        default=False,
    )

    show_master_ftp: BoolProperty(
        default=False,
    )

    show_master_smb: BoolProperty(
        default=False,
    )

    show_rs: BoolProperty(
        default=True,
    )

    show_rs_general: BoolProperty(
        default=True,
    )

    show_rs_advanced: BoolProperty( 
        default=False,
    )

    # General Settings

    #region master
    master_working_directory: StringProperty(
        default="//SRF/",
        name="Working Directory",
        description="The working directory for the render farm.\nRecommended: //SRF/",
        subtype="DIR_PATH",
    )

    master_logging: BoolProperty(
        default=False,
        name="Logging",
        description="Enable logging to a file.\nWarning: This can require a lot of disk space.\nRecommended: True",
    )

    master_port: IntProperty(
        default=19186,
        name="Port",
        min=1,
        max=65535,
        description="The port to use for the server.\nRecommended: 19186",
    )

    master_analytics: BoolProperty(
        default=False,
        name="Analytics",
        description="Enable analytics.",
    )

    master_data: BoolProperty(
        default=False,
        name="Save Debug Data",
        description="Saves debug data to a file.\nCompletely local, no data is sent anywhere.\nRecommended: True",
    )

    master_ipoverride: StringProperty(
        default="",
        name="IP Override",
        description="Override the IP address that the server binds to.\nLeave empty for automatic.",
    )

    master_prf_override: StringProperty(
        default="",
        name="PRF Override",
        description="Override the PRF file location.\nLeave empty for automatic.",
        subtype="DIR_PATH",
    )

    master_client_limit: IntProperty(
        default=0,
        name="Client Limit",
        min=0,
        description="Limit the number of clients that can connect.\n0 = No Limit",
    )

    master_ftp_url: StringProperty(
        default="",
        name="FTP URL",
        description="The URL to the FTP server.",
    )

    master_ftp_user: StringProperty(
        default="",
        name="FTP Username",
        description="The username to use for the FTP server.",
    )

    master_ftp_pass: StringProperty(
        default="",
        name="FTP Password",
        description="The password to use for the FTP server.",
        subtype="PASSWORD",
    )

    master_smb_url: StringProperty(
        default="",
        name="SMB URL",
        description="The URL to the SMB server.",
    )

    master_smb_user: StringProperty(
        default="",
        name="SMB Username",
        description="The username to use for the SMB server.",
    )

    master_smb_pass: StringProperty(
        default="",
        name="SMB Password",
        description="The password to use for the SMB server.",
        subtype="PASSWORD",
    )

    master_db_override: StringProperty(
        default="",
        name="Database Override",
        description="Override the database file location.\nLeave empty for automatic.",
        subtype="DIR_PATH",
    )
    #endregion master
    #region rendersettings
    rs_use_sfr: BoolProperty(
        default=False,
        name="Use SFR",
        description="Optimizes your render settings before rendering",
    )

    rs_use_sidt: BoolProperty(
        default=False,
        name="Use SID-Temporal",
        description="Denoise your animation using SID-Temporal",
    )

    rs_test_render: BoolProperty(
        default=False,
        name="Test Render",
        description="Render a test frame before rendering the full animation",
    )

    rs_batch_size: IntProperty(
        default=1,
        name="Batch Size",
        min=1,
        description="The number of frames to render at once",
    )

    rs_transfer_method: EnumProperty(
        items=(
            ("0", "TCP", "Transfer files using TCP"),
            ("1", "SMB", "Transfer files using SMB"),
            ("2", "FTP", "Transfer files using FTP"),
        ),
        default="0",
        name="Transfer Method",
        description="The method to use for transferring files",
    )

    rs_render_device: EnumProperty(
        items=(
            ("AUTO", "Automatic", "Let the client decide"),
            ("CPU", "CPU", "Render using the CPU"),

            ("OPTIX", "OptiX", "Render using OptiX (NVIDIA RTX)"),
            ("OPTIX+CPU", "OptiX + CPU", "Render using OptiX and the CPU"),
            ("CUDA", "CUDA", "Render using CUDA (NVIDIA)"),
            ("CUDA+CPU", "CUDA + CPU", "Render using CUDA and the CPU"),

            ("HIP", "HIP", "Render using HIP (AMD)"),
            ("HIP+CPU", "HIP + CPU", "Render using HIP and the CPU"),
            ("OPENCL", "OpenCL", "Render using OpenCL (AMD)"),
            ("OPENCL+CPU", "OpenCL + CPU", "Render using OpenCL and the CPU"),

            ("ONEAPI", "OneAPI", "Render using OneAPI (Intel)"),
            ("ONEAPI+CPU", "OneAPI + CPU", "Render using OneAPI and the CPU"),

            ("METAL", "Metal", "Render using Metal (Mac)"),
            ("METAL+CPU", "Metal + CPU", "Render using Metal and the CPU"),
        ),
        default="AUTO",
        name="Render Device",
        description="The device to use for rendering",
    )

    rs_close_blender: BoolProperty(
        default=False,
        name="Close Blender",
        description="Close Blender while rendering",
    )
    #endregion rendersettings
    #region others
    others_pull_frequency: IntProperty(
        default=5,
        name="Pull Frequency",
        min=1,
        soft_max=60,
        description="The frequency to pull new information from the server in seconds",
    )
    #endregion others

# Register

classes = (
    SRF_Settings,
)


def register_function():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.srf_settings = bpy.props.PointerProperty(type=SRF_Settings)

def unregister_function():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except (RuntimeError, Exception) as e:
                print(f"Failed to unregister {cls}: {e}")

    try:
        del bpy.types.Scene.srf_settings
    except:
        pass