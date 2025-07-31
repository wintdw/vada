import time
import logging

from typing import Dict

from .order import get_product_detail, get_orders


async def crawl_nhanh_data(
    business_id: str, access_token: str, from_date: str, to_date: str
) -> Dict:
    start_time = time.time()

    try:
        orders = []
        total_pages = 1
        page = 1

        while page <= total_pages:
            logging.debug(
                f"Fetching page {page} for orders from {from_date} to {to_date}"
            )
            # Get orders for the current page
            data = await get_orders(business_id, access_token, from_date, to_date, page)

            total_pages = data.get("totalPages", 1)
            returned_orders = data.get("orders", {})

            for order_id, order in returned_orders.items():
                # Map saleChannel to saleChannelName
                sale_channel_mapping = {
                    "1": "Admin",
                    "2": "Website",
                    "10": "API",
                    "20": "Facebook",
                    "21": "Instagram",
                    "41": "Lazada.vn",
                    "42": "Shopee.vn",
                    "43": "Sendo.vn",
                    "45": "Tiki.vn",
                    "46": "Zalo Shop",
                    "47": "1Landing.vn",
                    "48": "Tiktok Shop",
                    "49": "Zalo OA",
                    "50": "Shopee Chat",
                    "51": "Lazada Chat",
                }
                sale_channel = str(order.get("saleChannel", ""))
                order["saleChannelName"] = sale_channel_mapping.get(
                    sale_channel, "Unknown"
                )

                import_money = 0
                for product in order.get("products", []):
                    product_id = product.get("productId")
                    product["detail"] = await get_product_detail(
                        business_id, access_token, product_id
                    )
                    if product["detail"]["importPrice"]:
                        product["importMoney"] = int(
                            product["detail"]["importPrice"]
                        ) * int(product["quantity"])
                        import_money += product["importMoney"]
                order["TotalImportMoney"] = import_money

                orders.append(order)
            page += 1

        return {
            "status": "success",
            "total_orders": len(orders),
            "orders": orders,
            "date_start": from_date,
            "date_end": to_date,
            "execution_time": time.time() - start_time,
        }
    except Exception as e:
        logging.error(f"Error while crawling Nhanh data: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "date_start": from_date,
            "date_end": to_date,
            "execution_time": time.time() - start_time,
        }
