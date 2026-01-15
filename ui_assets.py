"""
UI Assets Module
Centralizes Base64 image strings and coordinate retrieval functions
to avoid code duplication between pet_manager and pet_analyzer.
"""
from image_search import search_image

# =============================================================================
# B64 IMAGE CONSTANTS
# =============================================================================

# Pet slots (8 pets in the pet window)
B64_PET_1 = "iVBORw0KGgoAAAANSUhEUgAAAAcAAAALCAYAAACzkJeoAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAC9SURBVChTXY9BDoIwEEXHhYalUNpCdW8IMRSoutCoZ/AkHEAu4FU8gUfyDJp8x4o1cfEzi/f/zB9yqxbnvgfRBLnJYWYmiNzaBai0gs50MNGiLDwUDK9RhAcRFBski6rG4tJ1uNMIN4ZPhn4tp8m2NXpO7miMg0w/0BjoPAMVyzLc3MZTD4WSiNlIVW0DPA5JwTNOBbfdrAP8rk14vkWN+/25F4mHkl/ybW1TezjnQqfhpuWU5buhEEf/RHgBRO97+iaKyk8AAAAASUVORK5CYII="  # Pet 1 slot
B64_PET_2 = "iVBORw0KGgoAAAANSUhEUgAAAAcAAAAKCAYAAAB4zEQNAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADLSURBVChTLU87CsJAFNyQDySRbPYfQew8hY1nsBCv4gU8gwhewDNY24kIgp3XEKtxdmMxPPbNm8+KrpeQWkM7BxtCghvGKbS1MN6PxHQY5/8tIrFRCs+iwDfL8OBc0sl6ko4Xp6bBuu8xo/WxrnEtSyg6Cj8MiAfJilhR9aGDtAYiLgwVMTteb7sO7zxPBYUyGpKZEZ6qOzN37YQCDyG1Qk9oEueqwoV51jr+gIWUMcnywCI3quaGX6MqtY15+7bFi8SCCsdlJFwI+AHAUmA4CuKu7gAAAABJRU5ErkJggg=="  # Pet 2 slot
B64_PET_3 = "iVBORw0KGgoAAAANSUhEUgAAAAYAAAANCAYAAACKCx+LAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADCSURBVChTbU47CsJQEHyRBEJ+5ftbiBjxEmIlFt7N0kawsFEPIJ5DbL2DCFYi40SjSWEx7O7MzuwK2/X4h0bwHoZoBA6LosC108FDCJyiCHMpP8JESQytQd85LPMclzCEMN4xgiCpWWfcvtFNR006ix5dmzTFOstqgTjGMcAb1a2xUq0oYkDXittnPiA0Y75C1U954x4ElWBRWgtHcmQM9kmCA2PfwpbDs87fsS+1hpD8RNGhWH89l4WkvU1UCdpZvAAboXHie0kmugAAAABJRU5ErkJggg=="  # Pet 3 slot
B64_PET_4 = "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAJCAYAAAD6reaeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACYSURBVBhXY1BQUfivqKrwXwmIldUUwZhBRkHmv6yi7H8lIP2AleX/HwaG/wxS8tL/QbhRiP//VTZWiKCkvNR/LVnJ/y+Ymf/HiAvDVEr9n83L/X8iP+9/JykxiKC1tPj/JyzM/1XlpICC4hDBbVyc/0tEBP9LAy2CC/4HEu+ZmP6/A+KPQAziMxgBtRvLSIBxuIQIUCXDfwAF20kNbSTFwQAAAABJRU5ErkJggg=="  # Pet 4 slot
B64_PET_5 = "iVBORw0KGgoAAAANSUhEUgAAAAcAAAALCAYAAACzkJeoAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAC3SURBVChTVZA9DoJQEIQXEgwxSEVB5D08Ayo/8hcsPQmHQOIhrOz1Gt7Ck9CajAsIeRTTzLe7s7uUZAWubQuiFYTvQ8hechCFaa7A3ai+gAspylQ4mjNM8wL3ugbThR62DcrKaoBfNuQ08p9LeXVeQKkulHDmBCdzkBCgfRguMjtdx9s0UbouKDge5m094SFg87Ve42MYfEoSK1Bg63m4OA46TeMnxBFuTYMNQ18KnLizH/u0LPwA/0l+iZL5GyQAAAAASUVORK5CYII="  # Pet 5 slot
B64_PET_6 = "iVBORw0KGgoAAAANSUhEUgAAAAQAAAAJCAYAAAAVb42gAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAB+SURBVBhXY5CSkfsvLSMLxwzSsnL/3cUl/u/g5Pz/jonpP4OPmPj/hyws/zOFhP9rS0n/ZzjGzv4/VFTsvwxMyx8Ghv+bOLnAyn8yMv5n+A8UKBAQ/K8uKQXRAhKQl5RG2PIXKOAMNFhKGiqwh4Pj/04Ozv8aElL/9SQk/wMAoec4ViJHMJcAAAAASUVORK5CYII="  # Pet 6 slot
B64_PET_7 = "iVBORw0KGgoAAAANSUhEUgAAAAcAAAAJCAYAAAD+WDajAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACnSURBVChTbY4tEsIwEIUzbVGkZUiTJt3dojgUVwCBw8H9OAICg2Cw3OCxybQO8dT3/gyJgFUkjEQJQxrggkMfehhiBoz5KzMyoYhGxBThY8DVrnFfNZrUOlKYZkjB41NVOLR2hmVvLHsXa/GoazjvMpRSmyFp8qXgpKntApfkedPhXVeIWu28vuUpQ4Go4dk0uHUtgjaEOMDIbkLWUZ1fPbKf3ycm/ADF2FtMblgRjgAAAABJRU5ErkJggg=="  # Pet 7 slot
B64_PET_8 = "iVBORw0KGgoAAAANSUhEUgAAAAYAAAALCAYAAABcUvyWAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADoSURBVChTZY67SgNRFEXPTDLJmIcG0RhGh7nzEkRFxMLCwl8QbNLrH9hYCPoZVn6CjZ0gNnamshBsBDtBOwkqCss92AgWGy6Xs9falmQJLnd/kuKKFNtdiLgNQz48j3dlpPdOPI+9+T4Hgz4rZcqGGqfTPZ6CAMOMLeHKxYxC2YsGvNRq2EW3w3O9zkl/hmPlVZ+Hc7PYWuF4aDb4Fr9qX7dbLFXym9YEl502m3nCMI54bAScT3Z/HasSV/y8zBhq5dj3sE8hjsReVn1dq856U9yFTWxfK+7l+NLBWNOv5Nh2MVbV/yfjB6YFbZSH/g5hAAAAAElFTkSuQmCC"  # Pet 8 slot

B64_PETS = [B64_PET_1, B64_PET_2, B64_PET_3, B64_PET_4, B64_PET_5, B64_PET_6, B64_PET_7, B64_PET_8]

# UI Buttons
B64_PET_TAB = "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAMCAYAAABSgIzaAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAHcSURBVChTTZJNaxNhFIUHRJf+AUHowoUK7qQ/oNRNXfoDXCi6cqMIbnRTEFcuCsVITR1S0mqotbE0ZTJIkgqpiY0xceJHGk3EJMaPIqjQYs3juZ2KDRwuvO99zj3vnTjs+nmXzjM6dJxe9jF01qH5AepNmF2A29NsjcVZv+HSvhbhP9jpUrx3F2f/PtzL5+DLZ1irQ60MM9OQllljDTLLbFyfErjZ34a+JRPUKk85dPgAsQunofdJjQLrb6AloK3pXelJFqIPBYqj/ZHxM6cYPHqQgb17CKKRbTNeBfBaar4LDd7L4EUHiumdqD82uXhiEMdxuHLsCL8DNbf0tkoJAkWtvZR0ZmoUZDon8Ksife9TmriJOzJMJzEnSJGCqtwFmirPVQWX39LvXmXr50mBvybDBbS1xVYrjFO1RoNWd8HqKevNjZjAEZxe4SzkU5DK60KNFs3qsxXY0AJy2mZBd0Xpn4G3qokrY/AgA0t+eFFTxJIge9efHdBLQ3JRfUmYV03MC8yq+ZEHi0vhJNukRa3q3KZ7ShPTd4xKd+JhnbHl5LUlT64GZ3LhVAPLOi8u61xTJqf0z4nBhGRg3MCUIF8f1VdcqznBJl/RfZnNassRAbekcVcGmure5y89lz3QdhqrtAAAAABJRU5ErkJggg=="           # Pet tab in skill bar
B64_CARRY = "iVBORw0KGgoAAAANSUhEUgAAADIAAAAXCAYAAABJXhw0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAL2SURBVFhH3dh5SFRBHAfw+aNQM20jj1a31M3UMl3RvK/SBMUDo0zSvJAKxRSsVAIj8ygV7FDTQDtEQSKo6NAg6C+VoMPEwlJMRbNc70Bdr2/vDbgsOrv7p/oGPjAz39/bmd23A2+XcA2C8Oh9D4SAJFS0QAiIc2IJhIDYhV2AEJB9AfEQAmLuEgIhIKb2ftAkNiUb7Z1dUCjmMTn9D/VPXzLr1hsxtvWAOrHnL2J8cgpxqVkwd/CFnWcwYrg5Vu16I6K99lCn8/sPpGddZWa8uHMZ6PrZA8X8PKa4u/Ww4QmMpTKaeQZFYnBoGKcSUzAwOISx8QlEJ6VqzT5+6UDx7XvKNYykjhifmERUQopyjoVs0dEDi6nYHHzbbSZh5jwvHz+4eXpB31AEqbUN2tu/IjEpmWYyZxfMzc2hta0NllJrXM7OQWfnN61ZWnoGuru7lWuEhIZDPjoKXX0D5RwL90a2cZ217B2dsLy8zMzUKSy6ibz8AtqXOR+m11tYWdOx7UEHvGlq1pqZcB+gQqGAh7cvHdfUPkBV9X3a14Rs1TMAi6W1Hb0jJuI9zJzn5XsELa1tmJmZobV8u15QRDMnF3csLi6uuUZbxnv2/AXulFdCd7sII3I5/AOCmHWqiI7BLqgzPPwH8UlnmRmvf2AAr5vewlQipeP8omKK7zu7+9DNqtav0JTxTkTH0rWDw4+jr78fuoZGzDpVRN9IAnVycvPwd0SOiKgY7DSzgmT/IYSfPK3Mp7kD/rihkWZ8TW9fPwpLymjm6htIN7tSq0pTxhOJLem5+NzegdJb5cya1cgOyQFokpVbgJ7ePswvLHAvPobaukZllpp5hbv1Y5jlDu6r5ncovVuNG2UVNPMIjKCbXalVpSlbUVVTR7+q7kfDmPlqxMjGDRtRZW09Wj58YmYsRCw7ho3E1icSyZnXMDM7h9AzacwaFiJxDcNGsrS0jF8Dv5F8qYCZq0MsvKMgBMTKPwZCwP0eSeCe5zc/subfiE2J4D9k6QIhKpOoewAAAABJRU5ErkJggg=="             # "Carry" button in pet window
B64_DETAILS = "iVBORw0KGgoAAAANSUhEUgAAADwAAAAWCAYAAACcy/8iAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAOWSURBVFhH5Zd7SFNRHMfPH0WZWUZTWS7TZStbpm1uM3WZWZSyHkQWSKlhBEVpWEEPKspHL5Ayi+gfjYgsqj+isOwd9CCizOxBL0wpKx+1leZj8u2cwzbvdXdqVH/dA5/t7Pf9nu/93bu7My4pvfkWcoKkF9+FnCC6jH2QE2SCZS3kBBk7Iw1yggTqk/A/mJiQIlnvD4bkNDR/tyJnZ6GrFpW0DM5h7+oS+f8EEqCdBiHxC9IdscCvtjY8rnqBjKytIk9fxFqWoqOjQ1LrD1rzfFS9eC15XNYfO+Ge9f5C/MZHQ4jZkgq7vYvPg6ckIDN7C378bMGSFetEvt4QZvxr/jab+AZpIWTqrAU8UFjL21+EG3fu8bkqzIiycxfwk16EpuZvOHSsBCNDwl1eT8OpL1uZjVev36Kd3gFW2w+UnDwDP3UE1yaaZjjc9Lbt0YMTqf4YlsUZqHr+Ep2ddt7bxm35bh4GGTDIC0IidHoaaBfVEhJnoaGxkc9PlZ1GSWkpRij8oTea8PnLF+Rs2CjyS2U4iYmbBuPUGHgP84U6VIPKyqfIWJ4p8vS23pPG+mA5g7194K8chaBgtZuHQU94CJ10E6GLcgR213QGE9rb2/lJMi1AqXJpBw4W4dbtOyK/VIYn8gv2YGdunqjW23pPWk1NDYoPH4EyMMhNE0IGeg3FQC8fF5F6Ew8U1mYnz8Wn+npMitQ7bjjxeFZdLfJLZTiJMU/H3Xv30dra6lgN7MorEHl6W+9JmxIVjYqr19FGN9ryKxX0whjdPOxcySCfkRCiM8XxQGHtYPERnDl7HoEhGt6gQjlGpPck0hCDLrqTeg33c9M+1NbiUvkVBKjU/HNuwV6O0CPVQ380hko9HiXHT6C2rk5SJ94KFYQYzIk8kM0DQ7VYv2kbrFYbr7Pag4ePcPxkGYInRMLHPwjjwqMwWhMuylCqw+jfUicyV2XBVxkMzWSDS7PRjYqtHzEqBPNSUvG+5gPy9xWK1gt76IknzTwzGQpVKM/dvH0X/U1/dfMwyHBVGIREJ87j3yIbVpsNl6/dQnzSIpeupTtpecUNtLS08h2xtu4j5ixcKspgrNu0A/X0oOybZu/O+uqcLfja0MT/4y9evob9RUexu7CYa6mZaxxH7h6sh740xqs373gm6+lJVbVkTwyi0BghJ4gyYibkBFEZLJATZExsCuQECYlPhZygz8Pp9DlRPhA62ItMIPgNOHy2EenKgQoAAAAASUVORK5CYII="           # "Details" button in pet window
B64_UPGRADE = "iVBORw0KGgoAAAANSUhEUgAAACIAAAAOCAYAAABKKc6PAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAMlSURBVEhLzZRrSFNhGMf3ISgptYuXlGW2VU7NRnM2bXPmpllt6jQ1HZjdbYVhUQlFQWFXSrpYQqaFUdmnKLx2sUBqGRaWthJiNdcS0tkqbVrTfzvP6BDLb36wF37w/Pm/z3v+73M4hyNaewL/Axz/cDnGkzhNHhzDw+D4hkRjPIlVa+FwOINMDQrHeBKTqHEFyddtRU9vL4xGIxYuEmHCRA9CmZgEg8GAkZER/L0mTfaEUBSJLrMZKZo0fDCZ0Gu1IjUtne3NXJ1NvUNDQ7DZvqL8UgU8pnixfiA3CDW1dRgcHCTf4XCAc6emDv5cHiouV6G2vhETPWfAyycA1r4+6AoK4e0biLPny/DFZiOPQSSROQ8Zgv5pC3iCCBTt3Y+O1wbWl8UvQ0ysgs6ZGypE28t2rNukY33mOeUVVzDNjwu1JsMVxD9YgMk+XCSlZMBq7aNaKJHT7b2nBpOWKVfA7kzP1AxRsUqa1LwIMemIKBka7j1gfXeOnTqDw8dPUR3AC6VefriItFiqcAXx5grgzQ2FdJkGg85RMvX02Qvw+k0ntu85AD+eEGUVV9H8pIU8hmhlCjX/0e4o1FnQP3sOu91OF2LW0ZJS8qKWqiiIa68A0QqVK4jP/MVgyNm8AyazhWrfEAmamvXofPceP3/9wtPWNkQq08hjiFXlOJuHWO1Ol6UbjU3N4IuVpE+cKyeYeqFcTcGCFy0lnbW+gM7iRCblIEyeDn3rK5RWViNAmIBoVS4+mD+BJ1GRdidv1Ub69kfzGL71D+DGrXoEiZcje0sRnXWyrIr1Ld2fUVR8GkuS89Dx9p0ryPeBHxj4YUf17bvgS9PBjVJj1uJkPHzSSsmZxYzS9LEbur3HyVdmb6MgTD0aOw+dRk+fjV51wyM9zlbeRMnF66yfV3gQ1i9fYeyyQLttn+uHNluaCXfCEteg3xlQosknzZdnY/eRC7B96/9n71gJinFeXqwCZ06cFu5IswpoEtrCYsxPWIOIlRtQXl2L9s73/+wdK8Gy1ZglSQWHr8jDaBSfvwZzdw+NjXl99x+/QJx216h7xwIvPtc5mUz8BimSz/Eusf/aAAAAAElFTkSuQmCC"           # "Upgrade" button in pet details
B64_CLOSE_PET = "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAQCAYAAAAvf+5AAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADvSURBVChTfZHdbsMgDEZ5nUmTpihNiMFAaNO/vf+zREpuvtrZGiUt28URwj76wGDaYGEF6gmdQNnDnRg2dWii1LMDy96M44gvqtBKQ7GJUHODQ2hWSZ1FVCpXo1NZUjRZBf8rLeI0TXjyUX+i8gf4ISCcw1pXzDzP2NIdPcIl7mrKm/gXpstUbGzREwzJUXqnkqCES1owTqT/RB4YLIMZfdySsGURS40Sb6KV4fTer/WdSCePVkR7lH9/kVfRnxnhGhFvPVhWviY4GWQnRmmkW0K69yvxnsHyfk/ZkCTRIN8mYv+df1BZkjU9SDINjAfNvNStW2DtFQAAAABJRU5ErkJggg=="         # Close pet window button (X)
B64_SAVE = "iVBORw0KGgoAAAANSUhEUgAAAC0AAAAUCAYAAAAZb7T/AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAATGSURBVEhL1Zd7TFNXHMdLxqP0bVvKUx7FsSIwnqtS5KUTJJDIBHXAiIDZErcswrKJ/+yRjbHIjHERMYM40I2MLTo3smDilrEZptE/mJtGN8ayBR8Ua0WhD17lu/s7t73Syf7ckJt8cs75/X739nPPPefeVDQ/P489e3ZBJBItC7JMJojq63eyQWLZXjR+Moiu/uFHEnIjR7e8CE9ufx11bedQe/gcdrT++EhCbuSYXPEWL51S1YS0mpZlQWp1My8dnJjLk5DzEKbi59D37Vncuz8Bl8uFMYsVLzU2LVr7n+P2ZNLKiHhoVqVDG2dE0BNrBcKTsmG+bcHet/dDn74BIatNSMnbjFSOhXX/B+RGjuTKpP2lKsh00VzAAFVkgkBaThHoiE7K9IovpPqF3fh1aBjTMzO4PzGJzu7PEaRPZrndjW/ixs1RrIhKFOqPHP0YX/WdYf2IeCN6TvbCZrPDencch9o7oYlJEmoXQm7kSK5M2jcgcFH8A6UYHPwJly9fwbZnKyCRKx+qMa3LgTHTBKlCBf2qOFy69DNqaneynDY4BE6nEzl569mYrndrdBTPlJWz8ac9n6GzqwsrtDqkG9fAPDaGV159Tbj2v+GWlsAvUMYh5+5EiQC52o0GmpBIvNO8D2bzGKxWK5r37YcyKIzlFoPyVO8Zn/jiS7R92MH6hSWlsFjuQKYOgTY0CnNzcwiNelyo/aC1DT+cHRDGHg9yIjdyJFcmTQOPrFipg0QdyhEGqTZCQBEchfLKGgz9PoxTvV8L8dyCEpy/cBEObkY9x7stB4Q8nWMeuw25LhIfHe9GW/tRFk/NzHNXex9Xrl4TziUHciGnB/Iyz5omYQ0rkGpXQh4SC0VYHFtHtPAXUlBaCbvdIYxHrt/E6W/6EbnayMbvHWhlePKa6ERY7lixpep53B2/h9yichaPTc5ikuGGDKHWGwNzIBdyIjdyJFcmTXdBQc9mVOtT2E6NzdiATdvqEJOWD51hLeJNm3Cs5xT6By6w3UxMTNrQfaIXYQlZ2Fr3Mv4auYGWQx1Cnmg/1oOrvw3j2tAfXvGLg7+wcw2Zhez6SdnFiDNuFPLkQC6eTciLq3lpsTKIPQ5KUqEuPgshSfkwFlVh+M8R2LiZdbnmYebe0d0n+5CQW4bQ5KcZ9W+8D4t1HFNT0zj93QAOdnRj/5HjQp4orNjFZrXpYIdXPKOwEme+Pw+7w4lZbn1fv2VGaW2DkCcHcuFfdQbmSK5MOlAVzD0GPdQxyawoNGUjwtOLEPFUyZJCDuRCTuRGjuQq8vHxYR1aP3RHdHcRGcWIzNyCqKytSwo5kAs5kRs5MmmaaVrcNP305QlLLcDKNZsRvW47YnIrlxRyIBdyIjdyZBuxoaGBzNmAFj09ErpLfX41YtfvWFLIgVzIidzcbw6wPwGNjS/yg2VATnY2RNrgcPj6Pgax2I/DHxJJAKRSMWQccpkYSoUECkUgQ6nk+9SqVFKWUymlXEzCx7i+pxXi7hzDXa905/lre8f5GP8bBOtTTM45cAQE+PEbkWZ7cnICDoeNe3XZMT3lwMy0kzE7O8XBt665ae7TS0zxcDGv1g3VsVp3nPp0Po0fXMfd/rOGaz35hb81O+OEw27jXOfxN5QCqpVfuIxjAAAAAElFTkSuQmCC"          # "Save" button in pet details

# =============================================================================
# AUTO MERGE IMAGES - Placeholders for user to fill
# =============================================================================

# Portal and Navigation
B64_PORTAL_ATHENS = "#"         # Portal to Athens image
B64_SEARCH = "#"                # Search button
B64_PET_MANAGER = "#"           # Pet Manager button

# Merge Interface
B64_MERGE = "#"                 # Merge button in pet window
B64_SLOT_A = "#"                # Letter "A" slot in merge interface
B64_SLOT_B = "#"                # Letter "B" slot in merge interface
B64_MERGING_PETS = "#"          # "Merging pets" button

# Bag Interface
B64_BAG = "#"                   # Bag button
B64_MERGED_SPIRIT = "#"         # Merged Spirit item in bag
B64_NEW_BAG = "#"               # "New bag" button/tab
B64_PET_IN_BAG = "#"            # Pet item in bag (for right-click collection)

# Close Interface
B64_CLOSE_INTERFACE = "#"       # Close interface button (X) - generic

# Mount and Travel
B64_MOUNT = "#"                 # Mount/dismount button
B64_TRANSPORTER_NPC = "#"       # Transporter NPC in Athens
B64_TRANSMIT = "#"              # Transmit button
B64_OK = "#"                    # OK button (confirmation dialogs)

# Destinations - Thermopylae path
B64_PARNITHA_PORT = "#"         # Parnitha Port destination option

# Destinations - Larissa path  
B64_THEBES = "#"                # Thebes destination option
B64_MYCENAE_TRANSPORTER = "#"   # Mycenae transporter NPC
B64_TRANSMIT_MYCENAE = "#"      # Transmit button in Mycenae
B64_GO_TO_MYCENAE = "#"         # "Go to Mycenae" option
B64_GO_TO_LARISSA = "#"         # "Go to Larissa" option

# SystemBar AFK Buttons
B64_THERMO_BTN = "#"            # Thermopylae button in SystemBar
B64_LARISSA_BTN = "#"           # Larissa button in SystemBar

# AFK Interface
B64_AFK = "#"                   # AFK button
B64_START_AFK = "#"             # Start button (for AFK mode)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_pet_coord(window, pet_index):
    """Get coordinates of a pet slot (0-7) with offset +20 in X"""
    if pet_index < 0 or pet_index >= 8:
        return None
    result = search_image(B64_PETS[pet_index], window)
    if result:
        return (result[0] + 20, result[1])  # +20 in X
    print(f"[DEBUG] get_pet_coord: Could not find PET_{pet_index + 1}")
    return None


def get_ui_coord(window, element_name):
    """Get coordinates of a UI element"""
    elements = {
        "PET_TAB": B64_PET_TAB,
        "CARRY": B64_CARRY,
        "DETAILS": B64_DETAILS,
        "SAVE": B64_SAVE,
        "CLOSE_PET": B64_CLOSE_PET,
        "UPGRADE": B64_UPGRADE,
        "PORTAL_ATHENS": B64_PORTAL_ATHENS,
        "SEARCH": B64_SEARCH,
        "PET_MANAGER": B64_PET_MANAGER,
        "MERGE": B64_MERGE,
        "SLOT_A": B64_SLOT_A,
        "SLOT_B": B64_SLOT_B,
        "MERGING_PETS": B64_MERGING_PETS,
        "BAG": B64_BAG,
        "MERGED_SPIRIT": B64_MERGED_SPIRIT,
        "NEW_BAG": B64_NEW_BAG,
        "PET_IN_BAG": B64_PET_IN_BAG,
        "CLOSE_INTERFACE": B64_CLOSE_INTERFACE,
        "MOUNT": B64_MOUNT,
        "TRANSPORTER_NPC": B64_TRANSPORTER_NPC,
        "TRANSMIT": B64_TRANSMIT,
        "OK": B64_OK,
        "PARNITHA_PORT": B64_PARNITHA_PORT,
        "THEBES": B64_THEBES,
        "MYCENAE_TRANSPORTER": B64_MYCENAE_TRANSPORTER,
        "TRANSMIT_MYCENAE": B64_TRANSMIT_MYCENAE,
        "GO_TO_MYCENAE": B64_GO_TO_MYCENAE,
        "GO_TO_LARISSA": B64_GO_TO_LARISSA,
        "THERMO_BTN": B64_THERMO_BTN,
        "LARISSA_BTN": B64_LARISSA_BTN,
        "AFK": B64_AFK,
        "START_AFK": B64_START_AFK,
    }
    b64 = elements.get(element_name)
    if b64:
        result = search_image(b64, window)
        if result:
            return result
        print(f"[DEBUG] get_ui_coord: Could not find {element_name}")
    return None
