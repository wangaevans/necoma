Core Functionality | All Views
=============================

This section provides detailed documentation on all the core functionalities of the `netconfapp`. Each view function corresponds to a specific operation that can be performed on network devices. The descriptions are aimed at providing a clear understanding of what each view does, how it interacts with other components, and any important considerations for use.

Configure Device
----------------
This view allows users to apply new configurations to a specific network device. The configuration is sent to the device, and if successful, a new version of the configuration is saved in the system.

.. autofunction:: netconfapp.views.configure_device

Connect to Device
-----------------
This view handles the initial connection to a network device. It captures the device details and attempts to connect using the provided credentials and vendor-specific drivers.

.. autofunction:: netconfapp.views.connect_to_device

Modify Device Connection
------------------------
This view enables users to modify the connection details of an existing device. Users can update the IP address, username, password, vendor, and port information.

.. autofunction:: netconfapp.views.modify_device_connection

View Devices by OS
------------------
This view displays devices grouped by their operating system (e.g., Cisco, Arista, Juniper). It helps users quickly locate devices based on their OS type.

.. autofunction:: netconfapp.views.view_devices_by_os

View Configurations
-------------------
This view lists all configurations associated with a specific device, allowing users to review and manage configuration versions.

.. autofunction:: netconfapp.views.view_configurations

Rollback Configuration
----------------------
This view enables users to rollback a device's configuration to a previous version. It ensures that configurations can be reverted if needed.

.. autofunction:: netconfapp.views.rollback_configuration

Dashboard
---------
The main dashboard view, displaying an overview of all network devices managed by the system.

.. autofunction:: netconfapp.views.dashboard

Delete Item
-----------
This view handles the deletion of a network device from the system. It logs the deletion action and ensures that the device is properly removed.

.. autofunction:: netconfapp.views.delete_item

Show Configuration Logs
-----------------------
This view displays a log of all configuration changes and actions performed on network devices. It provides an audit trail for network configurations.

.. autofunction:: netconfapp.views.show_configuration_logs

Configure Multiple Devices
--------------------------
This view allows users to apply a configuration to multiple devices simultaneously. Users can choose between providing commands directly or uploading a configuration file.

.. autofunction:: netconfapp.views.configure_multiple_devices

View Single Configuration
-------------------------
This view displays the details of a single configuration for a specific device, including the changes made and the user who applied them.

.. autofunction:: netconfapp.views.view_single_configuration
