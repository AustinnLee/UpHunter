import re
import logging
import pandas as pd
from bs4 import BeautifulSoup
from src.parsers.base import BaseParser

logger = logging.getLogger("UpworkParser")


class UpworkParser(BaseParser):
    def parse(self, html_content):
        if not html_content:
            return pd.DataFrame()

        soup = BeautifulSoup(html_content, "html.parser")

        # Upwork 职位列表通常在 article 标签或者特定的 section 里
        # 策略：找所有包含 job-tile 的元素
        cards = soup.find_all("article")
        if not cards:
            # 备用方案：通过 data-test 属性查找
            cards = soup.find_all(attrs={"data-test": "JobTile"})

        logger.info(f"🔍 页面中找到了 {len(cards)} 个职位卡片")

        data_list = []
        for card in cards:
            try:
                item = {}

                # 1. 标题 (Title)
                # 通常在 h3 -> a 里面
                title_tag = card.find("h3")
                item['title'] = title_tag.get_text(strip=True) if title_tag else "Unknown"

                # 2. 链接 (URL)
                link_tag = card.find("a", href=True)
                if link_tag:
                    href = link_tag['href']
                    # Upwork 有时给相对路径
                    if href.startswith("/"):
                        href = "https://www.upwork.com" + href
                    item['url'] = href.split('?')[0]  # 去掉问号后面的参数
                else:
                    item['url'] = ""

                # 3. 类型与预算 (Type & Budget)
                # 这些通常在 strong 标签或者特定的 li 里
                # 我们获取整个卡片的文本来做正则匹配，这样更稳
                full_text = card.get_text(" | ", strip=True)

                # 匹配 Hourly: $30.00-$50.00
                hourly_match = re.search(r'\$(\d{1,3}(?:,\d{3})*)\.?\d*-\$(\d{1,3}(?:,\d{3})*)\.?\d*', full_text)
                if hourly_match:
                    item['job_type'] = 'Hourly'
                    item['budget_min'] = int(hourly_match.group(1).replace(',', ''))
                    item['budget_max'] = int(hourly_match.group(2).replace(',', ''))
                else:
                    # 匹配 Fixed: $500
                    fixed_match = re.search(r'(?:Budget|Est\. Budget): \$([\d,]+)', full_text, re.I)
                    if fixed_match:
                        item['job_type'] = 'Fixed'
                        val = int(fixed_match.group(1).replace(',', ''))
                        item['budget_min'] = val
                        item['budget_max'] = val
                    else:
                        # 也许是 Hourly 单一价: $30.00/hr
                        hourly_single = re.search(r'\$(\d{1,3}(?:,\d{3})*)\.?\d*/hr', full_text)
                        if hourly_single:
                            item['job_type'] = 'Hourly'
                            val = int(hourly_single.group(1).replace(',', ''))
                            item['budget_min'] = val
                            item['budget_max'] = val
                        else:
                            item['job_type'] = 'Unknown'
                            item['budget_min'] = 0
                            item['budget_max'] = 0

                # 4. 发布时间
                # 匹配 "Posted 5 minutes ago"
                posted_match = re.search(r'Posted (.*?) ago', full_text)
                item['posted_time'] = posted_match.group(1) + " ago" if posted_match else "Unknown"

                # 5. 描述
                # Upwork 现在的描述通常在 data-test="job-description-text"
                desc_tag = card.find(attrs={"data-test": "job-description-text"})
                item['description'] = desc_tag.get_text(strip=True) if desc_tag else ""

                data_list.append(item)

            except Exception as e:
                logger.warning(f"⚠️ 解析出错: {e}")
                continue

        return pd.DataFrame(data_list)
