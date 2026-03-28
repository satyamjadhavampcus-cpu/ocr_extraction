from app.services.field_extractor import extract_fields_from_divs

layout_divs = [
    {'div_id':0,'type':'layout_block','content':'r\nDisability ili Supplier Diversity'},
    {'div_id':1,'type':'layout_block','content':'Disability:IN"'},
    {'div_id':2,'type':'layout_block','content':'Service Disabled Veteran Disability-Owned Business'},
    {'div_id':3,'type':'layout_block','content':'Enterprise'},
    {'div_id':4,'type':'layout_block','content':'certification has been met by'},
    {'div_id':5,'type':'layout_block','content':'Roberts & Ryan Investments, Inc.'},
    {'div_id':6,'type':'layout_block','content':'Authorized by Jill Houghton, President and CEO'},
    {'div_id':7,'type':'layout_block','content':'Disability:IN°'},
    {'div_id':8,'type':'layout_block','content':'This certificate is the property of the and must be returned, upon request of the Disability-iN™, if certification expires or is revoked.'}
]

result = extract_fields_from_divs(layout_divs)
print(result)
