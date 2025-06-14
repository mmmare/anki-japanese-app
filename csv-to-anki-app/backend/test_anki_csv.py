#!/usr/bin/env python3
"""
Test CSV parsing in Anki deck generator

This test script verifies that our CSV parsing works correctly with different formats:
1. Standard CSV files
2. Anki-format tab-separated files
3. Files with commas within data fields
"""
import os
import tempfile
import unittest
from app.services.anki_utils import create_anki_package_from_csv, fix_anki_csv_format
from app.services.deck_service import DeckService

class AnkiCSVParsingTest(unittest.TestCase):
    def setUp(self):
        self.deck_service = DeckService()
        self.temp_dir = tempfile.mkdtemp()
        self.test_outputs = []

    def tearDown(self):
        # Clean up any created files
        for file_path in self.test_outputs:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
                    
        if os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except:
                pass

    def test_standard_csv(self):
        """Test standard comma-separated CSV parsing"""
        csv_content = """Japanese,English,Reading,Example,Tags
猫,cat,ねこ,猫が好きです (I like cats),animal
犬,dog,いぬ,犬は友達です (Dogs are friends),animal
本,book,ほん,本を読みます (I read a book),object"""

        # Try creating an Anki package
        package = create_anki_package_from_csv(csv_content, "Standard CSV Test")
        
        # Write to file to verify it's valid
        output_path = os.path.join(self.temp_dir, "standard_csv_test.apkg")
        package.write_to_file(output_path)
        self.test_outputs.append(output_path)
        
        # Check that file was created
        self.assertTrue(os.path.exists(output_path), "APKG file was not created")
        self.assertGreater(os.path.getsize(output_path), 1000, "APKG file is too small")

    def test_anki_tab_format(self):
        """Test Anki-format tab-separated CSV parsing"""
        csv_content = """#separator:tab
#html:true
Japanese\tEnglish\tReading\tExample\tTags
猫\tcat\tねこ\t猫が好きです (I like cats)\tanimal
犬\tdog\tいぬ\t犬は友達です (Dogs are friends)\tanimal
本\tbook\tほん\t本を読みます (I read a book)\tobject"""

        # Try creating an Anki package
        package = create_anki_package_from_csv(csv_content, "Anki Tab Format Test")
        
        # Write to file to verify it's valid
        output_path = os.path.join(self.temp_dir, "anki_tab_format_test.apkg")
        package.write_to_file(output_path)
        self.test_outputs.append(output_path)
        
        # Check that file was created
        self.assertTrue(os.path.exists(output_path), "APKG file was not created")
        self.assertGreater(os.path.getsize(output_path), 1000, "APKG file is too small")

    def test_commas_in_fields(self):
        """Test CSV with commas within data fields"""
        csv_content = """Japanese,English,Reading,Example,Tags
猫,"cat, feline",ねこ,"猫が好きです, とても可愛いです (I like cats, they are very cute)",animal house
犬,"dog, canine",いぬ,"犬は友達です, 散歩が好きです (Dogs are friends, they like walks)","animal, pet"
本,"book, novel",ほん,"本を読みます, 面白いです (I read a book, it's interesting)",object library"""

        # Try creating an Anki package
        package = create_anki_package_from_csv(csv_content, "Commas In Fields Test")
        
        # Write to file to verify it's valid
        output_path = os.path.join(self.temp_dir, "commas_in_fields_test.apkg")
        package.write_to_file(output_path)
        self.test_outputs.append(output_path)
        
        # Check that file was created
        self.assertTrue(os.path.exists(output_path), "APKG file was not created")
        self.assertGreater(os.path.getsize(output_path), 1000, "APKG file is too small")

    def test_anki_format_with_commas(self):
        """Test Anki-format tab-separated CSV with commas within fields"""
        csv_content = """#separator:tab
#html:true
Japanese\tEnglish\tReading\tExample\tTags
猫\tcat, feline\tねこ\t猫が好きです, とても可愛いです (I like cats, they are very cute)\tanimal house
犬\tdog, canine\tいぬ\t犬は友達です, 散歩が好きです (Dogs are friends, they like walks)\tanimal, pet
本\tbook, novel\tほん\t本を読みます, 面白いです (I read a book, it's interesting)\tobject library"""

        # Try creating an Anki package
        package = create_anki_package_from_csv(csv_content, "Anki Format With Commas Test")
        
        # Write to file to verify it's valid
        output_path = os.path.join(self.temp_dir, "anki_format_with_commas_test.apkg")
        package.write_to_file(output_path)
        self.test_outputs.append(output_path)
        
        # Check that file was created
        self.assertTrue(os.path.exists(output_path), "APKG file was not created")
        self.assertGreater(os.path.getsize(output_path), 1000, "APKG file is too small")
        
    def test_fix_anki_csv_format(self):
        """Test that fix_anki_csv_format correctly processes Anki format files"""
        csv_content = """#separator:tab
#html:true
Japanese\tEnglish\tReading\tExample\tTags"""
        
        fixed_content = fix_anki_csv_format(csv_content)
        self.assertTrue(fixed_content.startswith("#separator:tab"), "Metadata was removed")
        self.assertTrue("Japanese\tEnglish\tReading\tExample\tTags" in fixed_content, "Header was removed")
        
    def test_deck_service_create_anki_package(self):
        """Test the DeckService.create_anki_package_from_csv method with complex CSV content"""
        # Create a CSV with mixed tab and comma separators
        csv_content = """#separator:tab
#html:true
Japanese\tEnglish\tReading\tExample\tTags
猫\tcat, a small carnivorous mammal\tねこ\t猫はかわいいです (Cats are cute)\tanimal pet
犬\tdog, man's best friend\tいぬ\t犬は忠実です (Dogs are loyal)\tanimal"""

        # Try creating an Anki package through the service
        package = self.deck_service.create_anki_package_from_csv(csv_content, "DeckService Test")
        
        # Write to file to verify it's valid
        output_path = os.path.join(self.temp_dir, "deck_service_test.apkg")
        package.write_to_file(output_path)
        self.test_outputs.append(output_path)
        
        # Check that file was created
        self.assertTrue(os.path.exists(output_path), "APKG file was not created")
        self.assertGreater(os.path.getsize(output_path), 1000, "APKG file is too small")

if __name__ == "__main__":
    unittest.main()
