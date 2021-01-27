"""Zowe Python Client SDK.

This program and the accompanying materials are made available under the terms of the
Eclipse Public License v2.0 which accompanies this distribution, and is available at

https://www.eclipse.org/legal/epl-v20.html

SPDX-License-Identifier: EPL-2.0

Copyright Contributors to the Zowe Project.
"""

from zowe.core_for_zowe_sdk import SdkApi
from zowe.core_for_zowe_sdk.exceptions import FileNotFound
import os
import inspect


class Files(SdkApi):
    """
    Class used to represent the base z/OSMF Files API.

    ...

    Attributes
    ----------
    connection
        connection object
    """

    def __init__(self, connection):
        """
        Construct a Files object.

        Parameters
        ----------
        connection
            The z/OSMF connection object (generated by the ZoweSDK object)
        """
        super().__init__(connection, "/zosmf/restfiles/")

        
    def list_files(self, path):
        """Retrieve a list of USS files based on a given pattern.

        Returns
        -------
        json
            A JSON with a list of dataset names matching the given pattern
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["params"] = {"path": path}
        custom_args["url"] = "{}fs".format(self.request_endpoint)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json
        
    def get_file_content(self, filepath_name):
        """Retrieve the content of a filename. The complete path must be specified.

        Returns
        -------
        json
            A JSON with the contents of the specified USS file
        """
        custom_args = self.create_custom_request_arguments()
        #custom_args["params"] = {"filepath-name": filepath_name}
        custom_args["url"] = "{}fs{}".format(self.request_endpoint,filepath_name)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json


    def list_dsn(self, name_pattern):
        """Retrieve a list of datasets based on a given pattern.

        Returns
        -------
        json
            A JSON with a list of dataset names matching the given pattern
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["params"] = {"dslevel": name_pattern}
        custom_args["url"] = "{}ds".format(self.request_endpoint)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def list_dsn_members(self, dataset_name):
        """Retrieve the list of members on a given PDS/PDSE.

        Returns
        -------
        json
            A JSON with a list of members from a given PDS/PDSE
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}/member".format(self.request_endpoint, dataset_name)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json['items']

    def get_dsn_content(self, dataset_name):
        """Retrieve the contents of a given dataset.

        Returns
        -------
        json
            A JSON with the contents of a given dataset
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self.request_endpoint, dataset_name)
        response_json = self.request_handler.perform_request("GET", custom_args)
        return response_json

    def write_to_dsn(self, dataset_name, data):
        """Write content to an existing dataset.

        Returns
        -------
        json
            A JSON containing the result of the operation
        """
        custom_args = self.create_custom_request_arguments()
        custom_args["url"] = "{}ds/{}".format(self.request_endpoint, dataset_name)
        custom_args["data"] = data
        custom_args['headers']['Content-Type'] = 'text/plain'
        response_json = self.request_handler.perform_request(
            "PUT", custom_args, expected_code=[204, 201]
        )
        return response_json

    def download_dsn(self, dataset_name, output_file):
        """Retrieve the contents of a dataset and saves it to a given file."""
        response_json = self.get_dsn_content(dataset_name)
        dataset_content = response_json['response']
        out_file = open(output_file, 'w')
        out_file.write(dataset_content)
        out_file.close()

    def upload_file_to_dsn(self, input_file, dataset_name):
        """Upload contents of a given file and uploads it to a dataset."""
        if os.path.isfile(input_file):
            in_file = open(input_file, 'r')
            file_contents = in_file.read()
            response_json = self.write_to_dsn(dataset_name, file_contents)
        else:
            raise FileNotFound(input_file)

    def delete_file(self, dataset_name, volume=None):
        """Delete sequential and partitioned data set on a z/OS system.

        Returns
        -------
        json
            A JSON with a status code of an operation <br/><br/>
            Status code 204 indicates success. A status code of 4nn or 5nn indicates that an error has occurred. <br/><br/>
            If the request is successfully executed, status code 204 indicates success and no content is returned.
        """
        custom_args = self.create_custom_request_arguments()
        payload = f'/-({volume})/{dataset_name}' if volume else f'/{dataset_name}'
        custom_args['url'] = f'{self.request_endpoint}ds{payload}'
        response_json = self.request_handler.perform_request('DELETE', custom_args, expected_code=[204])
        return response_json

    def allocate_dsn(
            self, dataset_name,
            volser=None,
            unit=None,
            dsorg='PS',
            alcunit='TRK',
            primary=1,
            secondary=1,
            dirblk=0,
            avgblk=None,
            recfm='FB',
            blksize=27920,
            lrecl=80,
            storclass=None,
            mgntclass=None,
            dataclass=None,
            dsntype=None,
            like=None
    ):
        """
        Create sequential and partitioned data sets on a z/OS system.

        :param dataset_name: Name of a z/OS data set that you are going to create
        :param volser: Volume serial
        :param unit: Device type
        :param dsorg: Data set organization (Default: PS)
        :param alcunit: Unit of space allocation (Default: TRK)
        :param primary: Primary space allocation (Default: 1)
        :param secondary: Secondary space allocation (Default: 1)
        :param dirblk: Number of directory blocks (Default: 0)
        :param avgblk: Average block size
        :param recfm: Record format (Default: FB)
        :param blksize: Block size (Default: 27920)
        :param lrecl: Record length (Defaukt: 80)
        :param storclass: Storage class
        :param mgntclass: Management class
        :param dataclass: Data class
        :param dsntype: Data set type
        :param like: Model data set name

        :return: A JSON with a status code of an operation <br/><br/>
                Status code 201 indicates success. A status code of 4nn or 5nn indicates that an error has occurred. <br/><br/>
                For a successful creating request, 201 Created with no content will be returned.
        """
        custom_args = self.create_custom_request_arguments()
        custom_args['url'] = f'{self.request_endpoint}ds/{dataset_name}'

        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        args_val = {}
        for item in args:
            if item in ['self', 'dataset_name']:
                continue
            if values[item] is None:
                continue
            else:
                args_val[item] = values[item]

        custom_args['json'] = args_val
        custom_args['headers']['Content-Type'] = 'application/json'

        response_json = self.request_handler.perform_request('POST', custom_args, expected_code=[201])
        return response_json
