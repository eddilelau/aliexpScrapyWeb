from django import template
register = template.Library()
from django.utils.html import format_html

@register.simple_tag
def circle_page(curr_page,loop_page,date):
    offset = abs(curr_page-loop_page)
    if offset<3 :
        if curr_page == loop_page:
            page_html="""
            <a href=\"?page={page}&date={date}\" 
            class="paginate_button current" aria-controls="table1" data-dt-idx="1" tabindex="0">
            <font color='white'>{page}</font></a>
            """.format(page=loop_page,date=date)
        else:
            page_html="""<a href=\"?page={page}&date={date}\"
            class="paginate_button current" aria-controls="table1" data-dt-idx="1" tabindex="0" style=\" background-color:rgb(255,255,255)\">
            <font color='gray'>{page}</font>
            </a>""".format(page=loop_page, date=date)
        return format_html(page_html)
    else:
       return ""

@register.simple_tag
def circlePageForInfring(curr_page,loop_page,date,needDate):
    offset = abs(curr_page-loop_page)
    if offset<3 :
        if curr_page == loop_page:
            page_html="""<a href=\"?page={page}&date={date}&needDate={needDate}\" 
            class="paginate_button current" aria-controls="table1" data-dt-idx="1" tabindex="0">
            <font color='white'>{page}</font>
            </a>""".format(page=loop_page,date=date,needDate=needDate)
        else:
            page_html="""<a href=\"?page={page}&date={date}&needDate={needDate}\"
            class="paginate_button current" aria-controls="table1" data-dt-idx="1" tabindex="0" style=\" background-color:rgb(255,255,255)\">
            <font color='gray'>{page}</font>
            </a>""".format(page=loop_page, date=date,needDate=needDate)
        return format_html(page_html)
    else:
       return ""

@register.simple_tag
def circlePageForCompeting(curr_page,loop_page,date,firstCategory ,secondCategory,salesFilter):
    offset = abs(curr_page-loop_page)
    if offset<3 :
        if curr_page == loop_page:
            page_html="""
            <a href=\"?salesFilter={salesFilter}&page={page}&date={date}&firstCategory={firstCategory}&secondCategory={secondCategory}\" 
            class="paginate_button current" aria-controls="table1" data-dt-idx="1" tabindex="0">
            <font color='white'>{page}</font></a>
            """.format(page=loop_page,date=date,firstCategory =firstCategory ,secondCategory=secondCategory,salesFilter=salesFilter)
        else:
            page_html="""
            <a href=\"?salesFilter={salesFilter}&page={page}&date={date}&firstCategory={firstCategory}&secondCategory={secondCategory}\" 
            class="paginate_button current" aria-controls="table1" data-dt-idx="1" tabindex="0" style=\" background-color:rgb(255,255,255)\">
            <font color='gray'>{page}</font></a>
            """.format(page=loop_page, date=date,firstCategory =firstCategory ,secondCategory=secondCategory,salesFilter=salesFilter)
        return format_html(page_html)
    else:
       return ""

@register.simple_tag
def circlePageForCompetingProductList(curr_page,loop_page,date,currentCatalog):
    offset = abs(curr_page-loop_page)
    if offset<3 :
        if curr_page == loop_page:
            page_html="""
            <a href=\"?page={page}&date={date}&catalogID={currentCatalog}\" 
            class="paginate_button current" aria-controls="table1" data-dt-idx="1" tabindex="0">
            <font color='white'>{page}</font></a>
            """.format(page=loop_page,date=date,currentCatalog=currentCatalog)
        else:
            page_html="""
            <a href=\"?page={page}&date={date}&catalogID={currentCatalog}\" 
            class="paginate_button current" aria-controls="table1" data-dt-idx="1" tabindex="0" style=\" background-color:rgb(255,255,255)\">
            <font color='gray'>{page}</font></a>
            """.format(page=loop_page, date=date,currentCatalog=currentCatalog)
        return format_html(page_html)
    else:
       return ""