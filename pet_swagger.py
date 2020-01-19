"""
__author__ = "Laura Forbes"
__version__ = "1.0.1"
__date__ = "19 January 2020"

This script its used to perform operations in the Swagger Petstore database (https://petstore.swagger.io/).

Please refer to the README accompanying this script to see how this script can be run.
"""

import argparse
import sys
import os
import datetime
import requests
import json

# Example pet
id_9574394 = 9574394
photo = "https://www.petfoodindustry.com/ext/resources/Images-by-month-year/18_08/dog-business-office-computer.jpg"
pet_9574394 = {"id": id_9574394,
         "category": {"id": 0, "name": "dog"},
         "name": "Ralph",
         "status": "availableForAdoption",
         "tags": [{"id": 0, "name": "ralph_{0}".format(id_9574394)}],
         "photoUrls": [photo]}


class SwaggerPet:
    """
    Methods to create, update, retrieve info about and delete pet ID entries in
        the Swagger Petstore database (https://petstore.swagger.io/).
    """

    def __init__(self):
        """
        Initialise common variables.
        """
        self.swagger_pet_url = "https://petstore.swagger.io/v2/pet"

        self.curl_headers = {"Accept": "application/json",
                             "Content-Type": "application/json"}

    def check_pet_id_exists(self, pet_id):
        """
        Description:
            Checks whether a record with the given pet ID exists in the database.
        Args:
            pet_id (int): Numerical ID of the pet to check.
        Returns:
            bool. True if exists, False if does not exist.
        """
        # This is returned if pet ID does not exist: {'message': 'Pet not found', 'code': 1, 'type': 'error'}
        msg = "message"
        lost_pet = "Pet not found"

        # Check if ID is valid; i.e. if it exists in the database
        check = self.get_pet_info(pet_id)

        if msg in check and lost_pet == check[msg]:
            return False
        return True

    def get_pet_info(self, pet_id):
        """
        Description:
            Retrieves the database record of the given pet ID.
        Args:
            pet_id (int): Numerical ID of the pet record to retrieve.
        Returns:
            dict. Database entry of the specified pet ID. If pet ID does not exist in
                the database, will return dictionary with message 'Pet not found'.
        """
        return requests.get("{0}/{1}".format(self.swagger_pet_url, pet_id)).json()

    def verify_pet_info(self, pet_details):
        """
        Description:
            Checks whether the given pet details match the details in the database.
        Args:
            pet_details (dict.): Dictionary containing the key/value pairs of the pet. See the README for what keys
                must be present in this dictionary. Note that this dictionary has nested dictionaries.
        Returns:
            bool. True if the given pet details match the details in
                the database. False if the details do not fully match.
        """
        pet_id = pet_details["id"]

        # Check pet ID record exists in the database
        if not self.check_pet_id_exists(pet_id):
            print("Pet ID '{0}' does not exist in the database...\n".format(pet_id))
            return False

        print("Verifying that the details for pet ID '{0}' are as expected in the database...\n".format(pet_id))
        pet_id_db = self.get_pet_info(pet_id)

        # Compare pet data expected with retrieved pet data
        pet_info_diff = cmp(pet_details, pet_id_db)  # 0 if identical, -1 if difference(s)
        # ^^ Could use unittest instead

        if pet_info_diff:
            return False
        return True

    def create_pet(self, pet_details):
        """
        Description:
            Creates an entry in the pet database with the given details.
        Args:
            pet_details (dict.): Dictionary containing the key/value pairs of the pet. See the README for what keys
                must be present in this dictionary. Note that this dictionary has nested dictionaries.
        Raises:
            Exception: If ID already exists in the database or if creation was not successful.
        """
        pet_id = pet_details["id"]

        # Check if pet already exists in database.
        if self.check_pet_id_exists(pet_id):
            raise Exception("Pet ID '{0}' already exists in the database. Here are the current details in "
                            "the database for this ID:\n{1}\nPlease choose 'update' if you would like to amend "
                            "these details.".format(pet_id, json.dumps(self.get_pet_info(pet_id), indent=2)))

        print("Creating pet ID '{0}'...\n".format(pet_id))
        requests.post(self.swagger_pet_url, headers=self.curl_headers, data=json.dumps(pet_details))

        # ## Assert that pet was created with correct data
        if not self.verify_pet_info(pet_details):
            raise Exception("Pet ID '{0}' was not created successfully. Here are the current details in the database "
                            "for this ID:\n{1}".format(pet_id, json.dumps(self.get_pet_info(pet_id), indent=2)))
            # Could return False here instead of raising exception

        print("Pet ID '{0}' successfully created with the following details:\n{1}\n".format(
            pet_id, json.dumps(pet_details)))

        return pet_details

    def update_pet_info(self, pet_details):
        """
        Description:
            Updates a pet ID record with the given details.
        Args:
            pet_details (dict.): Dictionary containing the key/value pairs of the pet. See the README for what keys
                must be present in this dictionary. Note that this dictionary has nested dictionaries.
        Raises:
            Exception: If ID does not exist in database or if update was not successful.
        """
        pet_id = pet_details["id"]

        # Check pet ID record exists in the database
        if not self.check_pet_id_exists(pet_id):
            raise Exception("Pet ID '{0}' does not exist in the database. "
                            "Please use a valid ID or create a new entry with this ID.".format(pet_id))

        print("Updating details for pet ID '{0}'...\n".format(pet_id))
        requests.put(self.swagger_pet_url, headers=self.curl_headers, data=json.dumps(pet_details))

        if not self.verify_pet_info(pet_details):
            raise Exception("Pet ID '{0}' was not updated successfully. Here are the current details in the "
                            "database:\n{1}".format(pet_id, json.dumps(self.get_pet_info(pet_id), indent=2)))
        print("Details of pet ID '{0}' updated successfully:\n{1}\n".format(pet_id, json.dumps(pet_details)))
        return pet_details

    def delete_pet_info(self, pet_id):
        """
        Description:
            Deletes the pet record for the given pet ID.
        Args:
            pet_id (int): Numerical ID of the pet whose details are to be removed from the database.
        Returns:
            (int): Returns -1 if ID to be deleted does not exist in the database. Returns 0 is deletion was successful.
        Raises:
            Exception: If ID record was not deleted successfully.
        """
        # Check if ID is valid; i.e. if it exists in the database
        if not self.check_pet_id_exists(pet_id):
            print("Pet ID '{0}' does not exist in the pet database. "
                  "Please enter an ID that exists in the system.\n".format(pet_id))
            return -1

        print("Removing the following pet entry:\n{0}\n".format(json.dumps(self.get_pet_info(pet_id))))
        requests.delete("{0}/{1}".format(self.swagger_pet_url, pet_id))

        # Ensure pet ID no longer exists in the system
        if self.check_pet_id_exists(pet_id):
            raise Exception("Deletion of pet with ID '{0}' seems to not have worked correctly. "
                            "Please check the system and try again.".format(pet_id))

        print("Pet ID '{0}' details removed successfully.\n".format(pet_id))
        return 0


if __name__ == '__main__':
    output_file = 'swagger_pet_{0}.txt'

    parser = argparse.ArgumentParser()
    parser.add_argument("-da", "--db_action", help="Action to perform on pet ID in database. "
                                                   "Options are: create, update, delete and info.")
    parser.add_argument("-if", "--input_file", help="Full path to local JSON file which contains pet details. This "
                        "option must be passed in when requesting database action 'create' or 'update'. Refer "
                                                    "to the README to see how this file should be formatted.")
    parser.add_argument("-pi", "--pet_id", help="ID of pet. Can only be used with database action 'delete' or 'info'.")
    parser.add_argument("-lf", "--log_file", action="store_true", help="Redirect the console output to a log. A log "
                        "file named '{0}' will be created in the directory where "
                            "the script is run from.".format(output_file.format("<TIMESTAMP>")))
    args = parser.parse_args()

    if args.log_file:
        # Redirect console output to a text file in the CWD
        timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")
        print("Console output of this script will be saved to '{0}'".format(output_file.format(timestamp)))
        sys.stdout = open(output_file.format(timestamp), 'w')

    # Default: Use example pet details.
    details_pet = pet_9574394
    example = True
    if args.input_file:
        example = False

        if not os.path.exists(args.input_file):
            sys.exit("Path '{0}' does not exist on this system. Please "
                     "pass in a valid path. Exiting...".format(args.input_file))

        with open(args.input_file, 'r') as in_file:
            details_pet = json.load(in_file)

    if args.pet_id:
        example = False

    swagger_pet = SwaggerPet()
    if example or args.db_action is not None and "create" in args.db_action:
        # Creates pet and verifies that it was created with the correct data
        swagger_pet.create_pet(details_pet)

    if example:
        details_pet["name"] = "Ruff"
        details_pet["tags"][0]["name"] = "{0}_{1}".format(details_pet["name"], id_9574394)
    if example or args.db_action is not None and "update" in args.db_action:
        # Updates pet details and verifies that it was updated with the correct data
        swagger_pet.update_pet_info(details_pet)

    id_pet = details_pet["id"]
    if args.pet_id is not None:
        id_pet = args.pet_id

    if example or args.db_action is not None and "delete" in args.db_action:
        # Deletes pet ID entry and asserts that the record no longer exists in the database
        swagger_pet.delete_pet_info(id_pet)

    if args.db_action is not None and "info" in args.db_action:
        print(json.dumps(swagger_pet.get_pet_info(id_pet)))
